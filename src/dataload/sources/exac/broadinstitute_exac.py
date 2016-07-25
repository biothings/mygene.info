from .broadinstitute_base import load_broadinstitute_exac

__metadata__ = {
    '__collection__': 'broadinstitute_exac',
}


def load_genedoc(self=None):
    genedoc_d = load_broadinstitute_exac()
    return genedoc_d


def get_mapping(self=None):
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
                        "index": "no",
                        },
                    "nontcga": {
                        "type": "object",
                        "index": "no",
                        },
                    "nonpsych": {
                        "type": "object",
                        "index": "no",
                        }
                    }
                }
            }
    return mapping
