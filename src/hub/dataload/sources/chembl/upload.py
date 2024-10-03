import copy
import glob
import os

import biothings.hub.dataload.storage as storage
import biothings.hub.dataload.uploader as uploader
from biothings.utils.dataload import merge_root_keys

from hub.datatransform.keylookup import MyGeneKeyLookup

from .parser import load_data


class ChemblMergerStorage(storage.RootKeyMergerStorage):
    """
    Just like MergerStorage, this storage deals with duplicated error
    by appending key's content to existing document. Keys in existing
    document will be converted to a list as needed.

    Note:
      - root keys must have the same type in each documents
      - inner structures aren't merged together, the merge happend
        at root key level
    """

    @classmethod
    def merge_func(klass, doc1, doc2, **kwargs):
        # caller popped it from doc1, let's take from doc2
        _id = doc2["_id"]
        # exclude_id will remove _if from doc2, that's why we kept it from before
        # also, copy doc2 ref as the merged doc will be stored in
        # a bulk op object, since doc2 is modified in place, this could impact
        # the bulk op and procude empty $set error from mongo
        doc = merge_root_keys(doc1, copy.copy(doc2), exclude=["_id", "xrefs"])
        doc["_id"] = _id
        return doc


class ChemblUploader(uploader.BaseSourceUploader):
    name = "chembl"

    storage_class = ChemblMergerStorage
    TARGET_FILENAME_PATTERN = "target.*.json"

    keylookup = MyGeneKeyLookup(
        input_types=[
            ("swissprot", "xrefs.accession"),
            ("trembl", "xrefs.accession"),
        ],
        skip_on_failure=True,
    )

    def load_data(self, data_folder):
        target_filepaths = glob.iglob(
            os.path.join(data_folder, self.TARGET_FILENAME_PATTERN)
        )
        # for doc in load_data(target_filepaths):
        #    yield doc
        return self.keylookup(load_data)(target_filepaths)

    @classmethod
    def get_mapping(klass):
        mapping = {
            "chembl_target": {
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer",
            },
            "xrefs": {
                "properties": {
                    "accession": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer",
                    },
                }
            },
        }
        return mapping
