from .parser import Gene2ECParser
import biothings.hub.dataload.uploader as uploader

class EntrezECUploader(uploader.MergerSourceUploader):

    name = "entrez_ec"
    main_source = "refseq"

    def load_data(self, data_folder):
        gene2ec = Gene2ECParser(data_folder).load()
        return gene2ec

    @classmethod
    def get_mapping(klass):
        mapping = {
            "ec": {
                "type": "keyword",
                "normalizer" : "keyword_lowercase_normalizer",
            },
        }
        return mapping
