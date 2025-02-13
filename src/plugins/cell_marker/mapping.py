def get_customized_mapping(cls):
    mapping = {
        "cellmarker": {
            "properties": {
                "cellontology": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword",
                },
                "pmid": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword",
                },
                "species": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword",
                },
                "uberon": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword",
                },
                "company": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword",
                },
                "marker_resource": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword",
                },
                "celltype": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword",
                },
                "tissue": {"type": "text"},
                "cancertype": {"type": "text"},
                "cellname": {"type": "text"},
            }
        }
    }
    return mapping
