import biothings.hub.dataload.uploader as uploader


class UnigeneUploader(uploader.DummySourceUploader):

    name = "unigene"

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
