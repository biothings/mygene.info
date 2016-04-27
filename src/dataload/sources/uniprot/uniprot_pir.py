from mongokit import OR
from uniprot_base import load_pir

__metadata__ = {
    '__collection__': 'uniprot_pir',
    'structure': {'pir': OR(unicode, list)},
}


def load_genedoc(self=None):
    return load_pir()


def get_mapping(self=None):
    mapping = {
        "pir": {
            "type": "string",
            "analyzer": "string_lowercase"
        }
    }
    return mapping
