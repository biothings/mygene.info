from .pharmgkb_base import load_pharmgkb

__metadata__ = {
    '__collection__': 'pharmgkb',
}


def load_data(self=None):
    return load_pharmgkb()


def get_mapping(self=None):
    mapping = {
        "pharmgkb": {
            "type": "string",
            "analyzer": "string_lowercase"
        }
    }
    return mapping
