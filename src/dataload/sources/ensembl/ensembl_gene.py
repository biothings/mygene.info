from .ensembl_base import EnsemblParser
from dataload import RootDocSourceUploader

class EnsemblGeneUploader(RootDocSourceUploader):

    name = "ensembl_gene"
    main_source = "ensembl"
    id_type = 'ensembl_gene'
    ENSEMBL_GENEDOC_ROOT = True

    def load_data(self, data_folder):
        ep = EnsemblParser(data_folder,load_ensembl2entrez=False)
        ensembl_genes = ep.load_ensembl_main()
        return ensembl_genes

    def get_mapping(self):
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
