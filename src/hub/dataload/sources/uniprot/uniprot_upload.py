import os

import biothings.hub.dataload.storage as storage
import biothings.hub.dataload.uploader as uploader
import biothings.utils.mongo as mongo

import config

from .parser import load_all, load_pdb, load_pir
from .pdb_upload import UniprotPDBUploader
from .pir_upload import UniprotPIRUploader


class UniprotUploader(uploader.MergerSourceUploader):
    name = "uniprot"
    main_source = "uniprot"

    def load_data(self, data_folder):
        genedoc_d = load_all(data_folder)
        return genedoc_d

    def post_update_data(self, *args, **kwargs):
        for field in ["uniprot.Swiss-Prot", "uniprot.TrEMBL"]:
            self.logger.info("Indexing '%s'" % field)
            self.collection.create_index(field, background=True)
        self.test()

    def test(self):
        # Retrieve collection statistics using the collStats command
        collection_stats = self.db.command("collStats", "uniprot")

        # Extract the count of documents from the statistics
        document_count = collection_stats["count"]

        self.logger.info("Number of documents in the collection %s", document_count)

        # Sanity check to see if documents are populated with Swiss-Prot and TrEMBL fields
        query = {"uniprot.Swiss-Prot": {"$exists": True}}
        swiss_prot_count = self.collection.count_documents(query)
        assert swiss_prot_count > 0, (
            "Swiss-Prot field in uniprot is missing. Swiss-Prot count: %s"
            % swiss_prot_count
        )

        query = {"uniprot.TrEMBL": {"$exists": True}}
        trembl_count = self.collection.count_documents(query)
        assert trembl_count > 0, (
            "TrEMBL field in uniprot is missing. TrEMBL count: %s" % trembl_count
        )

        # Sanity check using a stable _id
        test_id = self.collection.find_one({"_id": "1017"})
        assert (
            test_id.get("_id") == "1017"
        ), "Cannot find _id 1017 in uniprot collection"
        assert test_id.get("uniprot").get("TrEMBL"), (
            "Cannot find TrEMBL in _id 1017 in uniprot collection. test_id: %s"
            % test_id
        )
        assert test_id.get("uniprot").get("Swiss-Prot") == "P24941", (
            "Incorrect Swiss-Prot in _id 1017 in uniprot collection. test_id: %s"
            % test_id
        )

    @classmethod
    def get_mapping(klass):
        mapping = {
            "uniprot": {
                "dynamic": False,
                # "path": "just_name",
                "properties": {
                    "Swiss-Prot": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer",
                        "copy_to": ["all"],
                    },
                    "TrEMBL": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer",
                        "copy_to": ["all"],
                    },
                },
            }
        }
        return mapping
