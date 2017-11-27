import os

import config
import biothings.hub.dataindex.indexer as indexer


class GeneIndexer(indexer.Indexer):

    def get_index_creation_settings(self):
        return {"codec" : "best_compression",
                "auto_expand_replicas": "0-all"}

    def get_mapping(self, enable_timestamp=True):
        mapping = super(GeneIndexer,self).get_mapping(enable_timestamp)
        # mygene is "include everything" by default
        mapping.pop("include_in_all",None)
        return mapping
