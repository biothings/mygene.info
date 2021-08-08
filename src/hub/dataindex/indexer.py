from biothings.hub.dataindex.indexer import Indexer


class GeneIndexer(Indexer):

    def __init__(self, build_doc, indexer_env, target_name, index_name):
        super().__init__(build_doc, indexer_env, target_name, index_name)

        # add a tokenizer
        self.es_index_settings["analysis"]["tokenizer"] = {
            "refseq_tokenizer": {
                "delimiter": ".",
                "type": "path_hierarchy"
            }
        }
        # add an analyzer
        self.es_index_settings["analysis"]["analyzer"]["refseq_analyzer"] = {
            "filter": "lowercase",
            "tokenizer": "refseq_tokenizer",
            "type": "custom"
        }
