from entrez_base import Gene2AccessionParser

__metadata__ = {
    '__collection__': 'entrez_accession',
    'structure': {'accession': None}
}


def load_genedoc(self):
    parser = Gene2AccessionParser()
    parser.set_all_species()
    gene2acc = parser.load()
    return gene2acc


def get_mapping(self):
    mapping = {
        "accession": {"dynamic": False,
                      #"path": "just_name",      #make both fields, accession.rna and rna, work
                      "properties": {
                        "genomic": {
                            "type": "string",
                            "index": "no",
                            "include_in_all": False,
                            #"enabled": False,    #discard genomic for indexing
                        },
                        "rna": {
                            "type": "string",
                            "analyzer": "string_lowercase",
                            #"index_name": "accession",
                        },
                        'protein': {
                            "type": "string",
                            "analyzer": "string_lowercase",
                            #"index_name": "accession",
                        }
                      }

        }
    }
    return mapping
