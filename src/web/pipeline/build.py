import re

from elasticsearch_dsl import Search
from biothings.web.query import ESQueryBuilder, QueryPipelineException

from .legacy import dismax, interval, wildcard


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
            search = Search().from_dict(interval(**d))

        # query_string query
        elif q.startswith('"') and q.endswith('"') or \
                any(map(q.__contains__, (':', '~', ' AND ', ' OR ', 'NOT '))):
            search = Search().query(
                "query_string", query=q, default_operator="AND")

        # wildcard query
        elif '*' in q or '?' in q:
            search = Search().from_dict(wildcard(q))
        else:  # default query
            search = Search().from_dict(dismax(q))

        return search

    def apply_extras(self, search, options):

        search = Search().query(
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
            if 'all' in options.species:
                pass  # do not apply any filters
            elif not all(isinstance(string, str) for string in options.species):
                raise TypeError("species must be strings or integer strings.")
            elif not all(string.isnumeric() for string in options.species):
                raise QueryPipelineException(
                    code=400,
                    summary="cannot map some species to taxids."
                )
            else:  # filter by taxid numeric strings
                search = search.filter('terms', taxid=options.species)
        if options.aggs and options.species_facet_filter:
            search = search.post_filter('terms', taxid=options.species_facet_filter)

        return super().apply_extras(search, options)
