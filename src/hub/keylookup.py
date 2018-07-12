import networkx as nx
from biothings.utils.keylookup import KeyLookup

graph_mygene = nx.DiGraph()

graph_mygene.add_node('entrez')
graph_mygene.add_node('ensembl')
graph_mygene.add_node('uniprot')

graph_mygene.add_edge('swissprot', 'entrez',
        object={'col': 'uniprot',
            'lookup': 'uniprot.Swiss-Prot',
            'field': '_id'})

graph_mygene.add_edge('trembl', 'entrez',
        object={'col': 'uniprot',
            'lookup': 'uniprot.TrEMBL',
            'field': '_id'})

# TODO: conversions from ensembl to entrez should be added but mappings are currently
# computed and stored in mongo as files, not collections, so they can't be queried

class MyGeneKeyLookup(KeyLookup):
    collections = ['uniprot']
    def __init__(self, input_types, skip_on_failure=False):
        super(MyGeneKeyLookup, self).__init__(graph_mygene,
                self.collections, input_types,
                output_types=["entrez","ensembl"],
                skip_on_failure=skip_on_failure)

