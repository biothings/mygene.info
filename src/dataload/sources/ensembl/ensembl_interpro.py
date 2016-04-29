from .ensembl_base import EnsemblParser

__metadata__ = {
    '__collection__': 'ensembl_interpro',
    'structure': {'interpro': None},
    'id_type': 'ensembl_gene'
}


def load_genedoc(self=None):
    ep = EnsemblParser()
    ensembl2interpro = ep.load_ensembl2interpro()
    return ensembl2interpro


def get_mapping(self=None):
    mapping = {
        "interpro": {
            "dynamic": False,
            #"path": "just_name",
            "properties": {
                "id": {
                    "type": "string",
                    "analyzer": "string_lowercase",
                    #"index_name": "interpro"
                },
                "desc": {
                    "type": "string",
                    "index": "no",
                    "include_in_all": False
                },
                "short_desc": {
                    "type": "string",
                    "index": "no",
                    "include_in_all": False
                }
            }
        }
    }
    return mapping
