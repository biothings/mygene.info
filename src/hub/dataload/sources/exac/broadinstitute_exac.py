from .broadinstitute_base import load_broadinstitute_exac
import biothings.dataload.uploader as uploader

class ExacUploader(uploader.MergerSourceUploader):

    name = "broadinstitute_exac"
    main_source = "exac"

    def load_data(self, data_folder):
        genedoc_d = load_broadinstitute_exac(data_folder)
        return genedoc_d

    def get_mapping(self):
        mapping = {
                #do not index exons
                "exac": {
                    "dynamic": False,
                    #"path": "just_name",
                    "properties": {
                        "transcript": {
                            "type": "string",
                            "analyzer": "refseq_analyzer",
                            "include_in_all": False,
                            },
                        "n_exons": {
                            "type": "integer",
                            "index": "no",
                            },
                        "cds_start": {
                            "type": "integer",
                            "index": "no",
                            },
                        "cds_end": {
                            "type": "integer",
                            "index": "no",
                            },
                        "bp": {
                            "type": "integer",
                            "index": "no",
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
