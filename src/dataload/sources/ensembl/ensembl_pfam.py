from .ensembl_base import EnsemblParser

__metadata__ = {
    '__collection__': 'ensembl_pfam',
}


def load_data(self=None):
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
