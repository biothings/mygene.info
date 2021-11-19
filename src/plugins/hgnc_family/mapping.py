def get_customized_mapping(cls):
    mapping = {
        "hgnc_genegroup": {
            "properties": {
                "id": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "pubmed": {
                    "type": "integer"
                },
                "typical_gene": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "abbr": {
                    "type": "text"
                },
                "name": {
                    "type": "text"
                },
                "comments": {
                    "type": "text"
                }
            }
        }
    }

    return mapping
