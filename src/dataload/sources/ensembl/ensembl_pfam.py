from ensembl_base import EnsemblParser
from mongokit import OR

__metadata__ = {
    '__collection__': 'ensembl_pfam',
    'structure': {'pfam': OR(unicode, list)},
    # 'id_type': 'ensembl_gene',
}


def load_genedoc(self=None):
    ep = EnsemblParser()
    ensembl2pfam = ep.load_ensembl2pfam()
    return ensembl2pfam


def get_mapping(self=None):
    mapping = {
        "pfam": {
            "type": "string",
            "analyzer": "string_lowercase"
        }
    }
    return mapping
