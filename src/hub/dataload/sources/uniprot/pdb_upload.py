import biothings.hub.dataload.uploader as uploader
from .parser import load_pdb


class UniprotPDBUploader(uploader.MergerSourceUploader):

    name = "uniprot_pdb"

    def load_data(self, data_folder):
        return load_pdb(data_folder)

    @classmethod
    def get_mapping(klass):
        mapping = {
            "pdb": {
                "type": "keyword",
                "normalizer" : "keyword_lowercase_normalizer",
            }
        }
        return mapping

