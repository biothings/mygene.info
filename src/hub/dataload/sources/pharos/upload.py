import os

import biothings.hub.dataload.uploader as uploader

from .parser import load_data


class PharosUploader(uploader.BaseSourceUploader):
    name = "pharos"

    def load_data(self, data_folder):
        pharos_path = os.path.join(data_folder, "pharos_target_mapping.csv")
        pharos_tdl_path = os.path.join(data_folder, "pharos_tdl.csv")
        data = load_data(pharos_path, pharos_tdl_path)
        for doc in data:
            yield doc

    @classmethod
    def get_mapping(self):
        mapping = {
            "pharos": {
                "properties": {
                    "target_id": {"type": "integer"},
                    "tdl": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer",
                    },
                }
            }
        }
        return mapping
