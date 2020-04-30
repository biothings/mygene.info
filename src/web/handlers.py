
import requests

from biothings.utils.version import get_software_info
from biothings.web.handlers import MetadataSourceHandler, QueryHandler


class MygeneQueryHandler(QueryHandler):

    def pre_query_builder_hook(self, options):

        options = super().pre_query_builder_hook(options)
        if self.request.method == 'GET':
            if options.esqb.include_tax_tree and \
                    'all' not in options.esqb.species:
                headers = {
                    'user-agent': 'Python-requests_mygene.info/{} (gzip)'.format(
                        requests.__version__)}

                body = {
                    "ids": ','.join([str(sid) for sid in options.esqb.species]),
                    "expand_species": 'True'
                }
                res = requests.post(
                    self.web_settings.INCLUDE_TAX_TREE_REDIRECT_ENDPOINT, 
                    data=body, headers=headers)

                if res.status_code == requests.codes.ok:
                    options['esqb']['species'] = [str(x) for x in res.json()]
                    # logging.debug('tax_tree species: {}'.format(options.esqb_kwargs.species))

        return options


class MygeneSourceHandler(MetadataSourceHandler):
    """
    GET /metadata
    GET /v3/metadata

    {
        "app_revision": " ... ", # gitcommit hash
        "available_fields": "http://mygene.info/metadata/fields",
        "biothing_type": "gene",
        "build_date": "2020-03-29T04:00:00.012426",
        "build_version": "20200329",
        "genome_assembly": {
            "human": "hg38",
            "mouse": "mm10",
            ...
        },
        "source": null,
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

        appdir = self.web_settings.get_git_repo_path()
        commit = get_software_info(appdir).get('commit-hash', '')

        _meta['available_fields'] = 'http://mygene.info/metadata/fields'
        _meta['app_revision'] = commit
        _meta['genome_assembly'] = {}
        _meta['taxonomy'] = {}

        for s, d in self.web_settings.TAXONOMY.items():
            if 'tax_id' in d:
                _meta['taxonomy'][s] = int(d['tax_id'])
            if 'assembly' in d:
                _meta['genome_assembly'][s] = d['assembly']

        if "source" not in _meta:
            # occurs when loaded from scratch, not from a change/diff file
            _meta["source"] = None

        return _meta
