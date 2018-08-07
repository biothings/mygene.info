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
                            "type": "keyword",
                            "normalizer" : "keyword_lowercase_normalizer",
                            'copy_to': ['all'],
                            },
                        "gene": {
                            "type": "keyword",
                            "normalizer" : "keyword_lowercase_normalizer",
                            'copy_to': ['all'],
                            },
                        "protein": {
                            "type": "keyword",
                            "normalizer" : "keyword_lowercase_normalizer",
                            'copy_to': ['all'],
                            },
                        'translation': {
                            "type": "object",
                            "enabled": False,
                            },
                        "type_of_gene": {
                            "normalizer" : "keyword_lowercase_normalizer",
                            "type": "keyword"
                            },
                        }
                    }
                }
        return mapping
