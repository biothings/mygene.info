from .entrez_base import Gene2GeneRifParser
import biothings.dataload.uploader as uploader

class EntrezGenerifUploader(uploader.BaseSourceUploader):

    name = "entrez_generif"
    main_source = "entrez"

    def load_data(self, data_folder):
        gene2generif = Gene2GeneRifParser(data_folder).load()
        return gene2generif

    def get_mapping(self):
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
