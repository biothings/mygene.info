import copy
import glob
import os

import biothings.hub.dataload.storage as storage
import biothings.hub.dataload.uploader as uploader

from hub.datatransform.keylookup import MyGeneKeyLookup

from .parser import load_data


class ChemblMergerStorage(storage.MergerStorage):

    def merge_chembl(self, doc1, doc2):
        self.logger.info("Merging %s and %s", doc1, doc2)
        chembl_dict = {}

        for doc in [doc1, doc2]:
            chembl_list = doc.get("chembl", [])
            if not isinstance(chembl_list, list):
                chembl_list = [chembl_list]

            for chembl in chembl_list:
                uniprot = chembl.get("uniprot")
                chembl_target = chembl.get("chembl_target")

                if uniprot in chembl_dict:
                    if isinstance(chembl_dict[uniprot]["chembl_target"], list):
                        chembl_dict[uniprot]["chembl_target"].append(chembl_target)
                    else:
                        chembl_dict[uniprot]["chembl_target"] = [
                            chembl_dict[uniprot]["chembl_target"],
                            chembl_target,
                        ]
                else:
                    chembl_dict[uniprot] = {
                        "chembl_target": chembl_target,
                        "uniprot": uniprot,
                    }

        merged_doc = {"_id": doc2["_id"]}
        merged_doc["chembl"] = list(chembl_dict.values())
        self.logger.info("Merged doc: %s", merged_doc)
        return merged_doc

    @classmethod
    def merge_func(klass, doc1, doc2, **kwargs):
        instance = klass()
        doc = instance.merge_chembl(doc1, copy.copy(doc2))
        return doc


class ChemblUploader(uploader.BaseSourceUploader):
    name = "chembl"

    storage_class = ChemblMergerStorage
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
