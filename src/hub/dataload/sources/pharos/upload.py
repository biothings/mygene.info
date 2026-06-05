import glob
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
        # the TDL file is versioned (e.g. pharos400_tdls_full.csv), so glob for it
        matches = glob.glob(os.path.join(data_folder, "*tdls_full.csv"))
        if not matches:
            raise FileNotFoundError("No '*tdls_full.csv' file found in %s" % data_folder)
        pharos_path = matches[0]
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
