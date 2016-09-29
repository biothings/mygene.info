from .pharmgkb_base import load_pharmgkb
import biothings.dataload.uploader as uploader

class PharmgkbUploader(uploader.BaseSourceUploader):

    name = "pharmgkb"

    def load_data(self, data_folder):
        return load_pharmgkb(data_folder)

    def get_mapping(self):
        mapping = {
            "pharmgkb": {
                "type": "string",
                "analyzer": "string_lowercase"
            }
        }
        return mapping
