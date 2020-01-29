import biothings.hub.dataload.uploader as uploader


class EntrezUnigeneUploader(uploader.DummySourceUploader):

    name = "entrez_unigene"

    @classmethod
    def get_mapping(klass):
        mapping = {
            "unigene":  {
                "type": "keyword",
                "normalizer" : "keyword_lowercase_normalizer",
                'copy_to': ['all']
            }
        }
        return mapping
