import biothings.hub.dataload.uploader as uploader


class ChemblUploader(uploader.DummySourceUploader):
    name = "chembl"

    @classmethod
    def get_mapping(klass):
        mapping = {
            "chembl_target": {
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer",
            }
        }
        return mapping
