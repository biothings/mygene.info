from .ensembl_base import EnsemblParser
import biothings.dataload.uploader as uploader

class EnsemblPrositeUploader(uploader.MergerSourceUploader):

    name = "ensembl_prosite"
    main_source = "ensembl"
    id_type = 'ensembl_gene'

    def load_data(self, data_folder):
        ep = EnsemblParser(data_folder)
        ensembl2prosite = ep.load_ensembl2prosite()
        return ensembl2prosite

    def get_mapping(self):
        mapping = {
            "prosite": {
                "type": "string",
                "analyzer": "string_lowercase"
            }
        }
        return mapping
