from .parser import Gene2CDSParser
import biothings.hub.dataload.uploader as uploader

class EntrezCDSUploader(uploader.MergerSourceUploader):

    name = "entrez_cds"
    main_source = "refseq"

    def load_data(self, data_folder):
        gene2cds = Gene2CDSParser(data_folder).load()
        return gene2cds

    @classmethod
    def get_mapping(klass):
        mapping = {
            "cds": {
                "properties": {
                    "refseq": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "location": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "ccds": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    }
                }
            }
        }
        return mapping