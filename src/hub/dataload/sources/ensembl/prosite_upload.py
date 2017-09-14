from .parser import EnsemblParser
import biothings.hub.dataload.uploader as uploader

class EnsemblPrositeUploader(uploader.MergerSourceUploader):

    name = "ensembl_prosite"
    main_source = "ensembl"
    id_type = 'ensembl_gene'

    def load_data(self, data_folder):
        ep = EnsemblParser(data_folder)
        ensembl2prosite = ep.load_ensembl2prosite()
        return ensembl2prosite

    @classmethod
    def get_mapping(klass):
        mapping = {
            "prosite": {
                "type": "string",
                "analyzer": "string_lowercase"
            }
        }
        return mapping
