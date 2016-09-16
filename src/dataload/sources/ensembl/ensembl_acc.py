from .ensembl_base import EnsemblParser

__metadata__ = {
    '__collection__': 'ensembl_acc',
    #'id_type': 'ensembl_gene',
}


def load_data(self=None):
    ep = EnsemblParser()
    ensembl2acc = ep.load_ensembl2acc()
    return ensembl2acc


def get_mapping(self=None):
    mapping = {
            "ensembl": {
                "dynamic": False,
                #"path": "just_name",
                "properties": {
                    "transcript": {
                        "type": "string",
                        "analyzer": "string_lowercase",
                        },
                    "gene": {
                        "type": "string",
                        "analyzer": "string_lowercase",
                        },
                    "protein": {
                        "type": "string",
                        "analyzer": "string_lowercase",
                        },
                    'translation': {
                        "type": "object",
                        "enabled": False,
                        "include_in_all": False,
                        },
                    }
                }
            }
    return mapping
