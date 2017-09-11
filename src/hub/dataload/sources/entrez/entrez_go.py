from .entrez_base import Gene2GOParser
import biothings.dataload.uploader as uploader

class EntrezGOUploader(uploader.MergerSourceUploader):

    name = "entrez_go"
    main_source = "entrez"

    def load_data(self, data_folder):
        parser = Gene2GOParser(data_folder)
        parser.set_all_species()
        gene2go = parser.load()
        return gene2go

    def get_mapping(self):
        mapping = {
            "go": {
                "dynamic": False,
                "properties": {
                    "MF": {
                        "dynamic": False,
                        "properties": {
                            "term": {
                                "type": "string",
                                "include_in_all": False
                            },
                            "id": {
                                "type": "string",
                                "analyzer": "string_lowercase",
                            },
                            "evidence": {
                                "type": "string",
                                "index": "no"
                            },
                            "pubmed": {
                                "type": "long",
                                "index": "no"
                            }
                        }
                    },
                    "CC": {
                        "dynamic": False,
                        "properties": {
                            "term": {
                                "type": "string",
                                "include_in_all": False
                            },
                            "id": {
                                "type": "string",
                                "analyzer": "string_lowercase",
                            },
                            "evidence": {
                                "type": "string",
                                "index": "no"
                            },
                            "pubmed": {
                                "type": "long",
                                "index": "no"
                            }
                        }
                    },
                    "BP": {
                        "dynamic": False,
                        "properties": {
                            "term": {
                                "type": "string",
                                "include_in_all": False
                            },
                            "id": {
                                "type": "string",
                                "analyzer": "string_lowercase",
                            },
                            "evidence": {
                                "type": "string",
                                "index": "no"
                            },
                            "pubmed": {
                                "type": "long",
                                "index": "no"
                            }
                        }
                    }
                }
            }
        }
    
        return mapping
