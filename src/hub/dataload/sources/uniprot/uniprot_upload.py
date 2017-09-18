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

    def post_update_data(self, steps, force, batch_size, job_manager, **kwargs):
        # move produced files used for other dependent uploaders
        klass = {"pir":UniprotPIRUploader,"pdb":UniprotPDBUploader}
        release = os.path.split(self.data_folder)[-1]
        for ext in ["pir","pdb"]:
            destdir = os.path.join(config.DATA_ARCHIVE_ROOT,klass[ext].name,release)
            destfn = "gene2%s.pyobj" % ext
            try:
                os.makedirs(destdir)
            except FileExistsError:
                # good to go
                pass
            self.logger.info("Dispatching file '%s' to %s upload" % (destfn,ext.upper()))
            os.rename(os.path.join(self.data_folder,destfn),
                    os.path.join(destdir,destfn))
            uploader.set_pending_to_upload(klass[ext].name)

    @classmethod
    def get_mapping(klass):
        mapping = {
            "uniprot": {
                "dynamic": False,
                #"path": "just_name",
                "properties": {
                    "Swiss-Prot": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "TrEMBL": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    }
                }
            }
        }
        return mapping
