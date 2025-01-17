def get_customized_mapping(cls):
    mapping = {
        "agr": {
            "properties": {
                "orthologs": {
                    "properties": {
                        "geneid": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword",
                        },
                        "symbol": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword",
                        },
                        "CellOntologyID": {"normalizer": "keyword_lowercase_normalizer", "type": "keyword"},
                        "PMID": {"normalizer": "keyword_lowercase_normalizer", "type": "keyword"},
                        "speciesType": {"normalizer": "keyword_lowercase_normalizer", "type": "keyword"},
                        "UberonOntologyID": {"normalizer": "keyword_lowercase_normalizer", "type": "keyword"},
                        "Company": {"normalizer": "keyword_lowercase_normalizer", "type": "keyword"},
                        "cancerType": {"type": "text"},
                        "markerResource": {"type": "text"},
                        "tissueType": {"type": "text"},
                        "cellName": {"type": "text"},
                        "cellType": {"type": "text"},
                    }
                }
            }
        }
    }
    return mapping
