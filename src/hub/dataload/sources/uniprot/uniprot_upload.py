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
        self.logger.info("Indexing 'Swiss-Prot'")
        # background=true or it'll lock the whole database...
        self.collection.create_index("uniprot.Swiss-Prot",background=True)

    @classmethod
    def get_mapping(klass):
        mapping = {
            "uniprot": {
                "dynamic": False,
                #"path": "just_name",
                "properties": {
                    "Swiss-Prot": {
                        "type": "text",
                        "analyzer": "string_lowercase",
                        'copy_to': ['all'],
                    },
                    "TrEMBL": {
                        "type": "text",
                        "analyzer": "string_lowercase",
                        'copy_to': ['all'],
                    }
                }
            }
        }
        return mapping
