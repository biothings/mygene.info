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
                            "type": "text",
                            "analyzer": "string_lowercase",
                            'copy_to': ['all'],
                            },
                        "gene": {
                            "type": "text",
                            "analyzer": "string_lowercase",
                            'copy_to': ['all'],
                            },
                        "protein": {
                            "type": "text",
                            "analyzer": "string_lowercase",
                            'copy_to': ['all'],
                            },
                        'translation': {
                            "type": "object",
                            "enabled": False,
                            },
                        "type_of_gene": {
                            'analyzer': 'string_lowercase',
                            "type": "text"
                            },
                        }
                    }
                }
        return mapping
