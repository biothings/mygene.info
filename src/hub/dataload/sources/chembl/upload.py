import glob
import os

import biothings.hub.dataload.storage as storage
import biothings.hub.dataload.uploader as uploader

from hub.datatransform.keylookup import MyGeneKeyLookup

from .parser import load_data


class ChemblUploader(uploader.BaseSourceUploader):
    name = "chembl"

    storage_class = storage.RootKeyMergerStorage
    TARGET_FILENAME_PATTERN = "target.*.json"

    keylookup = MyGeneKeyLookup(
        input_types=[
            ("swissprot", "chembl.uniprot_accession"),
            ("trembl", "chembl.uniprot_accession"),
        ],
        skip_on_failure=True,
    )

    def load_data(self, data_folder):
        target_filepaths = glob.iglob(
            os.path.join(data_folder, self.TARGET_FILENAME_PATTERN)
        )
        return self.keylookup(load_data)(target_filepaths)

    @classmethod
    def get_mapping(klass):
        mapping = {
            "chembl": {
                "properties": {
                    "chembl_target": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer",
                    },
                    "uniprot_accession": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer",
                    },
                }
            },
        }
        return mapping
