"""
One search for a batch of IDs.

POST /v3/query and POST /v3/gene search each query term separately in an
msearch, with MygeneQueryBuilder.default_match_query weighted by species. For
the ID fields below, that query is biothings' multi_match. The symbol scope
gets the fixed scores from legacy.py instead, and keeps a search per term.
When every scope is an ID field, one terms query per field finds the same
genes for the whole batch with much less Elasticsearch CPU, and the hits are
split back by query term, in the order a search for each term returns them.
(On an index with more than one shard, the per-term searches' BM25 differs by
shard, so hits with equal weights could come in a different order. mygene's
index has one shard.)

A hit's _score is then its species weight times the highest boost of the
fields that matched its query term, instead of BM25.
"""

import copy
import re

from biothings.utils.common import dotdict
from biothings.web.query import ES_DEFAULT_SIZE, MAX_RESULT_WINDOW, AsyncESQueryPipeline, capturesESExceptions

# Scope fields looked up with terms queries, and the boost of a match on each.
# The per-term multi_match scores an entrezgene or ensembl.gene match with BM25,
# about 10 to 21 for an ID, and an _id or retired match with 1. Species weights
# run from 0.5 to 1.55, so any boost above 3.1 keeps that order: a gene whose
# current ID is the query term ranks above a gene that retired it.
ID_FIELD_BOOSTS = {"_id": 1, "entrezgene": 10, "ensembl.gene": 10, "retired": 1}

# Options one search can't reproduce for each term, and raw and rawquery, whose
# output shows the msearch. aggs, explain, fetch_all, scroll_id and search_after
# are GET options today, kept in case POST gains them.
MSEARCH_OPTIONS = (
    "from",
    "sort",
    "analyzer",
    "raw",
    "rawquery",
    "aggs",
    "explain",
    "fetch_all",
    "scroll_id",
    "search_after",
)

# numbers with a sign, a decimal point or an exponent: Elasticsearch turns some
# into a long to search retired, like 1017.0 into 1017
NUMBER = re.compile(r"[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?")
LONG_MAX = 2**63 - 1


def lookup_keys(term, scopes):
    """
    The (field, value) pairs that match a query term in its scopes, with values
    as Elasticsearch indexes them: _id as is, entrezgene and ensembl.gene in
    lowercase, retired as a long. None if a terms query can't match the term
    the way the per-term multi_match does.
    """
    if not term:
        return None  # the msearch rejects empty terms, and 0
    if isinstance(term, int) and not isinstance(term, bool):
        term = str(term)
    if not isinstance(term, str) or not term.isascii():
        return None  # Python and Lucene lowercase some non-ASCII letters differently
    if not isinstance(scopes, (list, tuple)) or not scopes:
        return None
    if not all(isinstance(field, str) and field in ID_FIELD_BOOSTS for field in scopes):
        return None

    keys = []
    for field in scopes:
        if field == "_id":
            keys.append((field, term))
        elif field != "retired":  # entrezgene and ensembl.gene, keywords with a lowercase normalizer
            keys.append((field, term.lower()))
        elif term.isdigit():
            digits = term.lstrip("0") or "0"
            if len(digits) <= 19 and int(digits) <= LONG_MAX:  # int() refuses more than 4,300 digits
                keys.append((field, int(digits)))
        elif NUMBER.fullmatch(term):
            return None
    return keys


class MygeneQueryPipeline(AsyncESQueryPipeline):
    """
    Search a batch of IDs with one query, see the module docstring.
    Other searches go through AsyncESQueryPipeline unchanged.
    """

    @capturesESExceptions
    async def search(self, q, **options):
        if isinstance(q, list):
            responses = await self.search_ids(q, dotdict(options))
            if responses is not None:
                # the templates AsyncESQueryPipeline.search sets for an msearch
                options["templates"] = (dict(query=_q) for _q in q)
                options["template_miss"] = dict(notfound=True)
                options["template_hit"] = dict()
                return self.formatter.transform(responses, **options)
        return await super().search(q, **options)

    async def search_ids(self, q, options):
        """
        Search the query terms in q with one query, and return an msearch-like
        response for each of them. Return None if the batch needs a search for
        each term: when a term or an option isn't supported, or when the hits
        don't all fit in one response.
        """
        if any(options.get(key) for key in MSEARCH_OPTIONS):
            return None
        if options.scopes:
            scoped = [(_q, options.scopes) for _q in q]
        elif options.autoscope and not any(isinstance(_q, (list, tuple)) for _q in q):
            # as ESQueryBuilder._build_one reads each term's scopes
            scoped = [self.builder.parser.parse(str(_q), self.builder.metadata) for _q in q]
        else:
            return None

        lookups = {}  # keys -> index, one lookup for terms with the same keys
        positions = []  # the lookup index of each query term
        for term, scopes in scoped:
            keys = lookup_keys(term, scopes)
            if keys is None:
                return None
            positions.append(lookups.setdefault(tuple(keys), len(lookups)))

        values = {}  # field -> values to look up
        owners = {}  # (field, value) -> indexes of the lookups with it
        for index, keys in enumerate(lookups):
            for field, value in keys:
                values.setdefault(field, set()).add(value)
                owners.setdefault((field, value), []).append(index)
        size = ES_DEFAULT_SIZE if options.size is None else options.size
        window = min(MAX_RESULT_WINDOW, len(lookups) * size)
        if not values or not window:
            return None

        search = self.builder.build_id_lookup({field: sorted(terms) for field, terms in values.items()}, options)
        search = search.extra(size=window, track_total_hits=False)
        docvalue_fields = [field for field in values if field != "_id"]
        if docvalue_fields:  # indexed values, to find the terms each hit matches
            search = search.extra(docvalue_fields=docvalue_fields)
        response = await self.backend.execute(search, **options)
        hits = response["hits"]["hits"]
        if len(hits) >= window:
            return None  # hits may be cut off, so fall back to a search for each term

        matches = [[] for _ in lookups]  # (score, hit) of each lookup
        for hit in hits:
            keys = [("_id", hit["_id"])]
            keys += [(field, value) for field, indexed in hit.pop("fields", {}).items() for value in indexed]
            boosts = {}  # lookup index -> highest boost of the fields it matched
            for key in keys:
                for index in owners.get(key, ()):
                    boosts[index] = max(boosts.get(index, 0), ID_FIELD_BOOSTS[key[0]])
            if not boosts:
                return None  # no term claims this hit, e.g. after a normalizer change
            for index, boost in boosts.items():
                matches[index].append((hit["_score"] * boost, hit))
        # sorted() is stable, so equal scores keep the order of the hits
        ranked = [sorted(found, key=lambda match: match[0], reverse=True) for found in matches]

        responses = []
        used = set()  # ids of the hits already given to a query term
        for index in positions:
            term_hits = []
            for score, hit in ranked[index][:size]:
                if id(hit) in used:
                    # each term sets its own _score, and the formatter changes hits in place
                    hit = copy.deepcopy(hit)
                used.add(id(hit))
                hit["_score"] = score
                term_hits.append(hit)
            responses.append({"hits": {"total": {"value": len(ranked[index])}, "hits": term_hits}})
        return responses
