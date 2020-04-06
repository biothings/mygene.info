
import requests

from biothings.utils.version import (get_repository_information,
                                     get_software_info)
from biothings.web.api.es.handlers import (QueryHandler,
                                           MetadataFieldHandler,
                                           MetadataSourceHandler)


class MygeneQueryHandler(QueryHandler):
    ''' This class is for the /query endpoint. '''

    def pre_query_builder_hook(self, options):

        if self.request.method == 'GET':
            if options.esqb.include_tax_tree and \
                    'all' not in options.esqb.species:
                headers = {
                    'user-agent': 'Python-requests_mygene.info/{} (gzip)'.format(requests.__version__)}

                body = {
                    "ids": ','.join([str(sid) for sid in options.esqb.species]),
                    "expand_species": 'True'
                }

                res = requests.post(
                    self.web_settings.INCLUDE_TAX_TREE_REDIRECT_ENDPOINT, data=body, headers=headers)

                if res.status_code == requests.codes.ok:
                    options['esqb']['species'] = [str(x) for x in res.json()]
                    # logging.debug('tax_tree species: {}'.format(options.esqb_kwargs.species))

        return options


class MygeneSourceHandler(MetadataSourceHandler):
    """
    GET /metadata
    GET /v3/metadata

    {
        "app_revision": "", # TODO
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

    def get(self):

        self.web_settings.read_index_mappings()
        res = self.web_settings.source_metadata[self.biothing_type]
        software = get_software_info(app_dir=self.web_settings.get_git_repo_path())

        if self.kwargs.source.dev:
            res['software'] = software

        res['available_fields'] = 'http://mygene.info/metadata/fields'
        res['app_revision'] = software.get('commit-hash', '')
        res['genome_assembly'] = {}
        res['taxonomy'] = {}

        for s, d in self.web_settings.TAXONOMY.items():
            if 'tax_id' in d:
                res['taxonomy'][s] = int(d['tax_id'])
            if 'assembly' in d:
                res['genome_assembly'][s] = d['assembly']

        if "source" not in res:
            # occurs when loaded from scratch, not from a change/diff file
            res["source"] = None

        self.finish(dict(sorted(res.items())))
