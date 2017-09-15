from .parser import load_all
import biothings.hub.dataload.uploader as uploader


class UniprotUploader(uploader.MergerSourceUploader):

    name = "uniprot"
    main_source = "uniprot"

    def load_data(self, data_folder):
        genedoc_d = load_all(data_folder)
        return genedoc_d

    def post_update_data(self, *args, **kwargs):
        uploader.set_pending_to_upload({"uniprot","upload_pdb"})
        uploader.set_pending_to_upload({"uniprot","upload_pir"})


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
