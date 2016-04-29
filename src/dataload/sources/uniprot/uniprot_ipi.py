from .uniprot_base import load_ipi

__metadata__ = {
    '__collection__': 'uniprot_ipi',
    'structure': {'ipi': None},
}


def load_genedoc(self=None):
    return load_ipi()


def get_mapping(self=None):
    mapping = {
        "ipi": {
            "type": "string",
            "analyzer": "string_lowercase"
        }
    }
    return mapping
