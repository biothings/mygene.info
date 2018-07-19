from .parser import load_data
import biothings.hub.dataload.uploader as uploader


class PharosUploader(uploader.BaseSourceUploader):
    name = "pharos"

    def load_data(self, data_file):
        return load_data(data_file)

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