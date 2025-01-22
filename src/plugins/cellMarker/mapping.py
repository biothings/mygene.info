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
                "cancertype": {"type": "text"},
                "marker_resource": {"type": "text"},
                "tissue": {"type": "text"},
                "cellname": {"type": "text"},
                "celltype": {"type": "text"},
            }
        }
    }
    return mapping
