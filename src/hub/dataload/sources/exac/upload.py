from .parser import load_broadinstitute_exac
import biothings.hub.dataload.uploader as uploader

class ExacUploader(uploader.MergerSourceUploader):

    name = "broadinstitute_exac"
    main_source = "exac"

    def load_data(self, data_folder):
        genedoc_d = load_broadinstitute_exac(data_folder)
        return genedoc_d

    @classmethod
    def get_mapping(klass):
        mapping = {
            #do not index exons
            "exac": {
                "dynamic": False,
                #"path": "just_name",
                "properties": {
                    "transcript": {
                        "type": "text",
                        "analyzer": "refseq_analyzer",
                        },
                    "n_exons": {
                        "type": "integer",
                        "index": False,
                        },
                    "cds_start": {
                        "type": "integer",
                        "index": False,
                        },
                    "cds_end": {
                        "type": "integer",
                        "index": False,
                        },
                    "bp": {
                        "type": "integer",
                        "index": False,
                        },
                    "all": {
                        "type": "object",
                        "enabled": False,
                        },
                    "nontcga": {
                        "type": "object",
                        "enabled": False,
                        },
                    "nonpsych": {
                        "type": "object",
                        "enabled": False,
                        }
                    }
                }
            }

        return mapping
