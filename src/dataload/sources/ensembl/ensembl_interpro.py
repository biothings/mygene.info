from .ensembl_base import EnsemblParser
import biothings.dataload.uploader as uploader

class EnsemblInterproUploader(uploader.MergerSourceUploader):

    name = "ensembl_interpro"
    main_source = "ensembl"
    id_type = 'ensembl_gene'

    def load_data(self, data_folder):
        ep = EnsemblParser(data_folder)
        ensembl2interpro = ep.load_ensembl2interpro()
        return ensembl2interpro

    def get_mapping(self):
        mapping = {
            "interpro": {
                "dynamic": False,
                #"path": "just_name",
                "properties": {
                    "id": {
                        "type": "string",
                        "analyzer": "string_lowercase",
                        #"index_name": "interpro"
                    },
                    "desc": {
                        "type": "string",
                        "index": "no",
                        "include_in_all": False
                    },
                    "short_desc": {
                        "type": "string",
                        "index": "no",
                        "include_in_all": False
                    }
                }
            }
        }
        return mapping
