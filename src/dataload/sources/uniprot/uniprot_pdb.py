from mongokit import OR
from uniprot_base import load_pdb

__metadata__ = {
    '__collection__': 'uniprot_pdb',
    'structure': {'pdb': OR(unicode, list)},
}


def load_genedoc(self=None):
    return load_pdb()


def get_mapping(self=None):
    mapping = {
        "pdb": {
            "type": "string",
            "index": "not_analyzed"     # PDB is case-sensitive here
        }
    }
    return mapping
