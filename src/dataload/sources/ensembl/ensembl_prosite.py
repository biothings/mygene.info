from .ensembl_base import EnsemblParser

__metadata__ = {
    '__collection__': 'ensembl_prosite',
    'id_type': 'ensembl_gene'
}


def load_data(self=None):
    ep = EnsemblParser()
    ensembl2prosite = ep.load_ensembl2prosite()
    return ensembl2prosite


def get_mapping(self=None):
    mapping = {
        "prosite": {
            "type": "string",
            "analyzer": "string_lowercase"
        }
    }
    return mapping
