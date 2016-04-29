from .ensembl_base import EnsemblParser

structure = {
                'ensembl': None,
            }
__metadata__ = {
    '__collection__' : 'ensembl_acc',
    #'structure': structure,
    #'required_fields' : ['ensembl'],
    #'id_type': 'ensembl_gene',
}

def load_genedoc(self=None):
    ep = EnsemblParser()
    ensembl2acc = ep.load_ensembl2acc()
    return ensembl2acc


def get_mapping(self=None):
    mapping = {
        "ensembl" : {"dynamic" : False,
                     #"path": "just_name",
                     "properties" : {
                     "transcript" : {
                        "type" : "string",
                        "analyzer": "string_lowercase",
                        #"index_name": "ensembltranscript",
                      },
                      "gene" : {
                        "type" : "string",
                        "analyzer": "string_lowercase",
                        #"index_name": "ensemblgene",
                      },
                      "protein" : {
                        "type" : "string",
                        "analyzer": "string_lowercase",
                        #"index_name": "ensemblprotein",
                      }
                    }
      },
    }
    return mapping
