import re

from biothings.utils.web.es_dsl import AsyncSearch
from biothings.web.pipeline import ESQueryBuilder

from .legacy import dismax, wildcard, interval


class MygeneQueryBuilder(ESQueryBuilder):


    def default_string_query(self, q, options):

        # genomic interval query
        pattern = r'chr(?P<chrom>\w+):(?P<gstart>[0-9,]+)-(?P<gend>[0-9,]+)'
        match = re.search(pattern, q)
        if match:  # (chr, gstart, gend)
            d = match.groupdict()
            if q.startswith('hg19.'):
                # support hg19 for human (default is hg38)
                d['assembly'] = 'hg19'
            if q.startswith('mm9.'):
                # support mm9 for mouse (default is mm10)
                d['assembly'] = 'mm9'
            search = AsyncSearch().from_dict(interval(**d))

        # query_string query
        elif q.startswith('"') and q.endswith('"') or \
                any(map(q.__contains__, (':', '~', ' AND ', ' OR ', 'NOT '))):
            search = AsyncSearch().query(
                "query_string", query=q,
                default_operator="AND",
                auto_generate_phrase_queries=True)

        # wildcard query
        elif '*' in q or '?' in q:
            search = AsyncSearch().from_dict(wildcard(q))
        else:  # default query
            search = AsyncSearch().from_dict(dismax(q))

        search = self._extra_query_options(search, options)
        return search

    def default_terms_query(self, q, scopes, options):

        search = super().default_terms_query(q, scopes, options)
        search = self._extra_query_options(search, options)
        return search

    def _extra_query_options(self, search, options):

        search = AsyncSearch().query(
            "function_score",
            query=search.query,
            functions=[
                {"filter": {"term": {"name": "pseudogene"}}, "weight": "0.5"},  # downgrade
                {"filter": {"term": {"taxid": 9606}}, "weight": "1.55"},
                {"filter": {"term": {"taxid": 10090}}, "weight": "1.3"},
                {"filter": {"term": {"taxid": 10116}}, "weight": "1.1"},
            ], score_mode="first")

        if options.entrezonly:
            search = search.filter('exists', field="entrezgene")
        if options.ensemblonly:
            search = search.filter('exists', field="ensembl.gene")

        if options.missing:
            for field in options.missing:
                search = search.exclude('exists', field=field)
        if options.exists:
            for field in options.exists:
                search = search.filter('exists', field=field)

        if options.species:
            if 'all' not in options.species:  # TODO
                search = search.filter('terms', taxid=options.species)
        if options.aggs and options.species_facet_filter:
            search = search.post_filter('terms', taxid=options.species_facet_filter)

        return search
