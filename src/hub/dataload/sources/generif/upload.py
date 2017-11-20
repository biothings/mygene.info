from .parser import Gene2GeneRifParser
import biothings.hub.dataload.uploader as uploader

class GenerifUploader(uploader.MergerSourceUploader):

    name = "generif"

    def load_data(self, data_folder):
        gene2generif = Gene2GeneRifParser(data_folder).load()
        return gene2generif

    @classmethod
    def get_mapping(klass):
        mapping = {
            # do not index generif
            "generif": {
                "properties": {
                    "pubmed": {
                        "type": "long",
                        "index": "no",
                    },
                    "text": {
                        "type": "string",
                        "index": "no",
                    }
                }
            }
        }
        return mapping
