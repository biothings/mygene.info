import biothings.hub.dataload.uploader as uploader

from .parser import Gene2GOParser


class EntrezGOUploader(uploader.MergerSourceUploader):

    name = "entrez_go"
    main_source = "entrez"

    def load_data(self, data_folder):
        parser = Gene2GOParser(data_folder)
        parser.set_all_species()
        gene2go = parser.load()
        return gene2go

    @classmethod
    def get_mapping(klass):
        mapping = {
            "go": {
                "dynamic": False,
                "properties": {
                    "MF": {
                        "dynamic": False,
                        "properties": {
                            "term": {
                                "type": "text",
                            },
                            "id": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer",
                                "copy_to": ["all"],
                            },
                            "evidence": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer",
                            },
                            "pubmed": {"type": "long", "index": False},
                            "category": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer",
                            },
                        },
                    },
                    "CC": {
                        "dynamic": False,
                        "properties": {
                            "term": {
                                "type": "text",
                            },
                            "id": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer",
                                "copy_to": ["all"],
                            },
                            "evidence": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer",
                            },
                            "pubmed": {"type": "long", "index": False},
                            "category": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer",
                            },
                        },
                    },
                    "BP": {
                        "dynamic": False,
                        "properties": {
                            "term": {
                                "type": "text",
                            },
                            "id": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer",
                                "copy_to": ["all"],
                            },
                            "evidence": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer",
                            },
                            "pubmed": {"type": "long", "index": False},
                            "category": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer",
                            },
                        },
                    },
                },
            }
        }

        return mapping
