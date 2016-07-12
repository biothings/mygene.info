from .uniprot_base import load_pir

__metadata__ = {
    '__collection__': 'uniprot_pir',
}


def load_data(self=None):
    return load_pir()


def get_mapping(self=None):
    mapping = {
        "pir": {
            "type": "string",
            "analyzer": "string_lowercase"
        }
    }
    return mapping
