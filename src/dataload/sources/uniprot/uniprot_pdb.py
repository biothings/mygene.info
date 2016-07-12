from .uniprot_base import load_pdb

__metadata__ = {
    '__collection__': 'uniprot_pdb',
}


def load_data(self=None):
    return load_pdb()


def get_mapping(self=None):
    mapping = {
        "pdb": {
            "type": "string",
            "index": "not_analyzed"     # PDB is case-sensitive here
        }
    }
    return mapping
