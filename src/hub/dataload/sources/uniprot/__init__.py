from .uniprot_base import load_all
import biothings.dataload.uploader as uploader

#UniProt id mapping source from UniProt directly
#ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/idmapping_selected.tab


class UniprotUploader(uploader.MergerSourceUploader):

    name = "uniprot"
    main_source = "uniprot"

    def load_data(self, data_folder):
        genedoc_d = load_all(data_folder)
        return genedoc_d

    def get_mapping(self):
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
