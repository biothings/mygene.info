import os

import config
import biothings.hub.dataindex.indexer as indexer


class GeneIndexer(indexer.Indexer):

    def get_index_creation_settings(self):
        settings = super(GeneIndexer,self).get_index_creation_settings()
        # mygene's specific
        settings["codec"] = "best_compression"
        settings["auto_expand_replicas"] = "0-all"
        settings["analysis"]["tokenizer"] = {
                "refseq_tokenizer": {
                    "delimiter": ".",
                    "type": "path_hierarchy"
                    }
                }
        settings["analysis"]["analyzer"]["refseq_analyzer"] = {
                "filter": "lowercase",
                "tokenizer": "refseq_tokenizer",
                "type": "custom"
                }

        return settings

