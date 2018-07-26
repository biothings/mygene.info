import networkx as nx
from biothings.utils.keylookup import KeyLookup

graph_mygene = nx.DiGraph()

graph_mygene.add_node('entrez')
graph_mygene.add_node('ensembl')
graph_mygene.add_node('uniprot')

for field in ["mgi","hgnc","rgd","tair","wormbase","zfin","sgd","flybase"]:
    graph_mygene.add_node(field)


graph_mygene.add_edge('swissprot', 'entrez',
        object={'col': 'uniprot',
            'lookup': 'uniprot.Swiss-Prot',
            'field': '_id'})

graph_mygene.add_edge('trembl', 'entrez',
        object={'col': 'uniprot',
            'lookup': 'uniprot.TrEMBL',
            'field': '_id'})

# TODO: GeneID already contains entrez _id but we need to keep
# the interface until keylookup is able to take from values
# from docs
graph_mygene.add_edge('GeneID', 'entrez',
        object={'col': 'entrez_gene',
            'lookup': '_id',
            'field': '_id'})

for field in ["MGI","HGNC","RGD","TAIR","WormBase","ZFIN","SGD","FLYBASE"]:
    graph_mygene.add_edge(field.lower(), 'entrez',
            object={'col': 'entrez_gene',
                'lookup': field,
                'field': '_id'})


# TODO: conversions from ensembl to entrez should be added but mappings are currently
# computed and stored in mongo as files, not collections, so they can't be queried

import pprint
pprint.pprint(graph_mygene)

class MyGeneKeyLookup(KeyLookup):
    collections = ['entrez_gene','uniprot']
    def __init__(self, input_types, skip_on_failure=False):
        super(MyGeneKeyLookup, self).__init__(graph_mygene,
                self.collections, input_types,
                output_types=["entrez","ensembl"],
                skip_on_failure=skip_on_failure)

