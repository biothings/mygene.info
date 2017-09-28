import os

import config
import biothings.hub.dataindex.indexer as indexer


class GeneIndexer(indexer.Indexer):

    def get_index_creation_settings(self):
        return {"codec" : "best_compression"}

