import biothings.hub.dataload.uploader as uploader
from .parser import load_pir


class UniprotPIRUploader(uploader.MergerSourceUploader):

    name = "uniprot_pir"

    def load_data(self, data_folder):
        return load_pir(data_folder)

    @classmethod
    def get_mapping(klass):
        mapping = {
            "pir": {
                "type": "keyword",
                "normalizer" : "keyword_lowercase_normalizer",
                'copy_to': ['all'],
            }
        }
        return mapping
