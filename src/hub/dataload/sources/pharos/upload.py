import biothings.hub.dataload.uploader as uploader

class PharosUploader(uploader.DummySourceUploader):
    name = "pharos"

    @classmethod
    def get_mapping(self):
        mapping = {
            "pharos": {
                "properties": {
                    "target_id":  {"type": "integer"}
                }
            }
        }
        return mapping
