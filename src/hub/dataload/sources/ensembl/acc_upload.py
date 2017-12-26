from .parser import EnsemblParser
import biothings.hub.dataload.uploader as uploader

class EnsemblAccUploader(uploader.MergerSourceUploader):

    name = "ensembl_acc"
    main_source = "ensembl"

    def load_data(self, data_folder):
        ep = EnsemblParser(data_folder)
        ensembl2acc = ep.load_ensembl2acc()
        return ensembl2acc

    @classmethod
    def get_mapping(klass):
        mapping = {
                "ensembl": {
                    "dynamic": False,
                    #"path": "just_name",
                    "properties": {
                        "transcript": {
                            "type": "string",
                            "analyzer": "string_lowercase",
                            },
                        "gene": {
                            "type": "string",
                            "analyzer": "string_lowercase",
                            },
                        "protein": {
                            "type": "string",
                            "analyzer": "string_lowercase",
                            },
                        'translation': {
                            "type": "object",
                            "enabled": False,
                            "include_in_all": False,
                            },
                        "type_of_gene": {
                            "index": "not_analyzed",
                            "type": "string",
                            "include_in_all": False},
                        }
                    }
                }
        return mapping
