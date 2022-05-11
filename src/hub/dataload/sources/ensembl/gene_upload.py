from .parser import EnsemblParser
import biothings.hub.dataload.uploader as uploader
from biothings.utils.common import dump2gridfs


class EnsemblGeneUploader(uploader.MergerSourceUploader):

    name = "ensembl_gene"
    main_source = "ensembl"
    __metadata__ = {"mapper": 'ensembl2entrez'}

    def load_data(self, data_folder):
        ep = EnsemblParser(self.main_source, data_folder, load_ensembl2entrez=False)
        ensembl_genes = ep.load_ensembl_main()
        return ensembl_genes

    def get_mapping_to_entrez(self, data_folder):
        ep = EnsemblParser(self.main_source, data_folder)
        ep._load_ensembl2entrez_li(self.main_source)
        return ep.ensembl2entrez_li

    def post_update_data(self, *args, **kwargs):
        self.logger.info('Uploading "mapping2entrezgene" to GridFS...')
        x2entrezgene_list = self.get_mapping_to_entrez(self.data_folder)
        dump2gridfs(x2entrezgene_list, self.name + '__2entrezgene_list.pyobj', self.db)

    @classmethod
    def get_mapping(klass):
        mapping = {
            "taxid": {"type": "integer"},
            "symbol": {
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer",
                "copy_to": "all"
            },
            "name": {
                "type": "text",
                "copy_to": "all"
            }
        }
        return mapping
