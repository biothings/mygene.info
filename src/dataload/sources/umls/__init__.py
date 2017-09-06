from .umls_base import load_umls

__metadata__ = {
    '__collection__': 'umls',
}


def load_genedoc(self=None):
    return load_umls()


def get_mapping(self=None):
    mapping = {
        "umls": {
            "properties": {
                "cui": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
            }
        }
    }
    return mapping
