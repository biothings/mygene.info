import networkx as nx
from biothings.hub.datatransform.datatransform_mdb import DataTransformMDB, MongoDBEdge

graph_mygene = nx.DiGraph()

for field in [
    "entrez",
    "ensembl",
    "uniprot",
    "mgi",
    "hgnc",
    "rgd",
    "tair",
    "zfin",
    "sgd",
    "flybase",
]:
    graph_mygene.add_node(field)


graph_mygene.add_edge(
    "swissprot",
    "entrez",
    object=MongoDBEdge("uniprot", lookup="uniprot.Swiss-Prot", field="_id"),
)

graph_mygene.add_edge(
    "swissprot",
    "swissprot",
    object=MongoDBEdge(
        "uniprot", lookup="uniprot.Swiss-Prot", field="uniprot.Swiss-Prot"
    ),
)

graph_mygene.add_edge(
    "trembl",
    "entrez",
    object=MongoDBEdge("uniprot", lookup="uniprot.TrEMBL", field="_id"),
)

# TODO: GeneID already contains entrez _id but we need to keep
# the interface until keylookup is able to take from values
# from docs
graph_mygene.add_edge(
    "entrez", "entrez", object=MongoDBEdge("entrez_gene", lookup="_id", field="_id")
)

for field in ["MGI", "HGNC", "RGD", "TAIR", "ZFIN", "SGD", "FLYBASE"]:
    graph_mygene.add_edge(
        field.lower(),
        "entrez",
        object=MongoDBEdge("entrez_gene", lookup=field, field="_id"),
    )


# TODO: conversions from ensembl to entrez should be added but mappings are currently
# computed and stored in mongo as files, not collections, so they can't be queried

import pprint

pprint.pprint(graph_mygene)


class MyGeneKeyLookup(DataTransformMDB):

    def __init__(self, input_types, skip_on_failure=False):
        super(MyGeneKeyLookup, self).__init__(
            graph_mygene,
            input_types,
            output_types=["entrez", "ensembl"],
            skip_on_failure=skip_on_failure,
        )
