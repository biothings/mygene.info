from .parser import Gene2GOParser
import biothings.hub.dataload.uploader as uploader

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
                                "normalizer" : "keyword_lowercase_normalizer",
                                'copy_to': ['all'],
                            },
                            "evidence": {
                                "type": "text",
                                "index": False
                            },
                            "pubmed": {
                                "type": "long",
                                "index": False
                            },
                            "category": {
                                "type": "text",
                                "index": False
                            }
                        }
                    },
                    "CC": {
                        "dynamic": False,
                        "properties": {
                            "term": {
                                "type": "text",
                            },
                            "id": {
                                "type": "keyword",
                                "normalizer" : "keyword_lowercase_normalizer",
                                'copy_to': ['all'],
                            },
                            "evidence": {
                                "type": "text",
                                "index": False
                            },
                            "pubmed": {
                                "type": "long",
                                "index": False
                            },
                            "category": {
                                "type": "text",
                                "index": False
                            }
                        }
                    },
                    "BP": {
                        "dynamic": False,
                        "properties": {
                            "term": {
                                "type": "text",
                            },
                            "id": {
                                "type": "keyword",
                                "normalizer" : "keyword_lowercase_normalizer",
                                'copy_to': ['all'],
                            },
                            "evidence": {
                                "type": "text",
                                "index": False
                            },
                            "pubmed": {
                                "type": "long",
                                "index": False
                            },
                            "category": {
                                "type": "text",
                                "index": False
                            }
                        }
                    }
                }
            }
        }

        return mapping
