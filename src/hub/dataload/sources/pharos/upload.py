import os

import biothings.hub.dataload.storage as storage
import biothings.hub.dataload.uploader as uploader
from hub.datatransform.keylookup import MyGeneKeyLookup

from .parser import load_data


class PharosUploader(uploader.BaseSourceUploader):
    name = "pharos"

    storage_class = storage.RootKeyMergerStorage
    keylookup = MyGeneKeyLookup(
        input_types=[
            ("swissprot", "pharos.uniprot"),
            ("trembl", "pharos.uniprot"),
        ],
        skip_on_failure=True,
    )

    def load_data(self, data_folder):
        pharos_path = os.path.join(data_folder, "current_tdls.csv")
        return self.keylookup(load_data)(pharos_path)

    @classmethod
    def get_mapping(self):
        mapping = {
            "pharos": {
                "properties": {
                    "tdl": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer",
                    },
                    "uniprot": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer",
                    },
                }
            }
        }
        return mapping
