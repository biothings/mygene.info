from .entrez_base import Gene2ECParser
import biothings.dataload.uploader as uploader

class EntrezECUploader(uploader.BaseSourceUploader):

    name = "entrez_ec"
    main_source = "entrez"

    def load_data(self, data_folder):
        gene2ec = Gene2ECParser(data_folder).load()
        return gene2ec

    def get_mapping(self):
        mapping = {
            "ec": {
                "type": "string",
                "analyzer": "string_lowercase",
                "include_in_all": False
            },
        }
        return mapping
