from .parser import EnsemblParser
import biothings.hub.dataload.uploader as uploader

class EnsemblInterproUploader(uploader.MergerSourceUploader):

    name = "ensembl_interpro"
    main_source = "ensembl"
    __metadata__ = {"mapper" : 'ensembl2entrez'}

    def load_data(self, data_folder):
        ep = EnsemblParser(data_folder)
        ensembl2interpro = ep.load_ensembl2interpro()
        return ensembl2interpro

    @classmethod
    def get_mapping(klass):
        mapping = {
            "interpro": {
                "dynamic": False,
                "properties": {
                    "id": {
                        "type": "keyword",
                        "normalizer" : "keyword_lowercase_normalizer",
                        'copy_to': ['all'],
                    },
                    "desc": {
                        "type": "text",
                        "index": False,
                    },
                    "short_desc": {
                        "type": "text",
                        "index": False,
                    }
                }
            }
        }
        return mapping
