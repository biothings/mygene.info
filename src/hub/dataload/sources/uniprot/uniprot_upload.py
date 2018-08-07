import os

from .parser import load_all, load_pir, load_pdb
import biothings.hub.dataload.uploader as uploader
import biothings.hub.dataload.storage as storage
import biothings.utils.mongo as mongo
import config

from .pdb_upload import UniprotPDBUploader
from .pir_upload import UniprotPIRUploader

class UniprotUploader(uploader.MergerSourceUploader):

    name = "uniprot"
    main_source = "uniprot"

    def load_data(self, data_folder):
        genedoc_d = load_all(data_folder)
        return genedoc_d

    def post_update_data(self, *args, **kwargs):
        for field in ["uniprot.Swiss-Prot","uniprot.TrEMBL"]:
            self.logger.info("Indexing '%s'" % field)
            self.collection.create_index(field,background=True)

    @classmethod
    def get_mapping(klass):
        mapping = {
            "uniprot": {
                "dynamic": False,
                #"path": "just_name",
                "properties": {
                    "Swiss-Prot": {
                        "type": "keyword",
                        "normalizer" : "keyword_lowercase_normalizer",
                        'copy_to': ['all'],
                    },
                    "TrEMBL": {
                        "type": "keyword",
                        "normalizer" : "keyword_lowercase_normalizer",
                        'copy_to': ['all'],
                    }
                }
            }
        }
        return mapping
