
import requests

from biothings.web.handlers import MetadataSourceHandler, QueryHandler


class MygeneQueryHandler(QueryHandler):

    async def get(self, *args, **kwargs):

        if self.args.include_tax_tree and 'all' not in self.args.species:

            res = requests.post(
                self.settings['biothings'].INCLUDE_TAX_TREE_REDIRECT_ENDPOINT,
                data={
                    "ids": ','.join([str(sid) for sid in self.args.species]),
                    "expand_species": 'True'
                },
                headers={
                    'user-agent': (
                        'Python-requests_'
                        'mygene.info/'
                        '{} (gzip)'
                    ).format(requests.__version__)
                })

            if res.status_code == requests.codes.ok:
                self.args.species = [str(x) for x in res.json()]

        await super().get(self, *args, **kwargs)


class MygeneSourceHandler(MetadataSourceHandler):
    """
    GET /metadata
    GET /v3/metadata

    {
        "biothing_type": "gene",
        "build_date": "2020-03-29T04:00:00.012426",
        "build_version": "20200329",
        "genome_assembly": {
            "human": "hg38",
            "mouse": "mm10",
            ...
        },
        "src": { ... }, // 28 items
        "stats": {
            "total": 36232158,
            "total_genes": 36232158,
            "total_entrez_genes": 27119488,
            "total_ensembl_genes": 38915576,
            "total_ensembl_genes_mapped_to_entrez": 5954466,
            "total_ensembl_only_genes": 9112670,
            "total_species": 28605
        },
        "taxonomy": {
            "human": 9606,
            "mouse": 10090,
            ...
        }
    }
    """

    def extras(self, _meta):

        _meta['taxonomy'] = {}
        _meta['genome_assembly'] = {}

        for s, d in self.biothings.config.TAXONOMY.items():
            if 'tax_id' in d:
                _meta['taxonomy'][s] = int(d['tax_id'])
            if 'assembly' in d:
                _meta['genome_assembly'][s] = d['assembly']

        return _meta
