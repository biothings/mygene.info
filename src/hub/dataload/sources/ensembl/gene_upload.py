from .parser import EnsemblParser
import biothings.hub.dataload.uploader as uploader

class EnsemblGeneUploader(uploader.MergerSourceUploader):

    name = "ensembl_gene"
    main_source = "ensembl"
    id_type = 'ensembl'
    ENSEMBL_GENEDOC_ROOT = True

    def load_data(self, data_folder):
        ep = EnsemblParser(data_folder,load_ensembl2entrez=False)
        ensembl_genes = ep.load_ensembl_main()
        return ensembl_genes

    @classmethod
    def get_mapping(klass):
        mapping = {
            "taxid":  {"type": "integer",
                       "include_in_all": False},
            "symbol": {"type": "string",
                       "analyzer": "string_lowercase",
                       "boost": 5.0},
            "name":   {"type": "string",
                       "boost": 0.8},    # downgrade name field a little bit
        }
        return mapping

    def get_mapping_to_entrez(self, data_folder):
        ep = EnsemblParser(data_folder)
        ep._load_ensembl2entrez_li()
        return ep.ensembl2entrez_li

    def generate_doc_src_master(self):
        # TODO: not sure this ENTREZ_GENEDOC_ROOT is actually useful now we're using class inheritance
        _doc = super(uploader.MergerSourceUploader,self).generate_doc_src_master()
        _doc["ENSEMBL_GENEDOC_ROOT"] = True

    def post_update_data(self):
        self.logger.info('Uploading "mapping2entrezgene" to GridFS...')
        x2entrezgene_list = self.get_mapping_to_entrez(self.data_folder)
        dump2gridfs(x2entrezgene_list, self.name + '__2entrezgene_list.pyobj', self.db)
