from biothings.hub.dataindex.indexer import Indexer


class GeneIndexer(Indexer):

    def __init__(self, build_doc, indexer_env, target_name, index_name):
        super().__init__(build_doc, indexer_env, target_name, index_name)
        self.index_settings["codec"] = "best_compression"  # mygene's specific
        self.index_settings["number_of_replicas"] = 0
        self.index_settings["number_of_shards"] = 3
        self.index_settings["analysis"]["tokenizer"] = {
            "refseq_tokenizer": {
                "delimiter": ".",
                "type": "path_hierarchy"
            }
        }
        self.index_settings["analysis"]["analyzer"]["refseq_analyzer"] = {
            "filter": "lowercase",
            "tokenizer": "refseq_tokenizer",
            "type": "custom"
        }
