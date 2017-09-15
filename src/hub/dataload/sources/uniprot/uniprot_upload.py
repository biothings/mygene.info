from .parser import load_all, load_pir, load_pdb
import biothings.hub.dataload.uploader as uploader
import biothings.hub.dataload.storage as storage
import biothings.utils.mongo as mongo



class UniprotUploader(uploader.MergerSourceUploader):

    name = "uniprot"
    main_source = "uniprot"

    def load_data(self, data_folder):
        genedoc_d = load_all(data_folder)
        return genedoc_d

    def post_update_data(self, steps, force, batch_size, job_manager, **kwargs):
        pir_data = load_pir(self.data_folder)
        pir_storage = storage.MergerStorage(mongo.get_src_db(),"uniprot_pir",self.logger)
        pir_storage.process(pir_data,batch_size)
        pdb_data = load_pdb(self.data_folder)
        pdb_storage = storage.MergerStorage(mongo.get_src_db(),"uniprot_pdb",self.logger)
        pdb_storage.process(pdb_data,batch_size)

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
