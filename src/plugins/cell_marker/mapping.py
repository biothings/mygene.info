def get_customized_mapping(cls):
    mapping = {
        "cellmarker": {
            "properties": {
                "cancertype": {"normalizer": "keyword_lowercase_normalizer", "type": "keyword"},
                "cellname": {"normalizer": "keyword_lowercase_normalizer", "type": "keyword"},
                "cellontology": {"normalizer": "keyword_lowercase_normalizer", "type": "keyword"},
                "celltype": {"normalizer": "keyword_lowercase_normalizer", "type": "keyword"},
                "marker_resource": {"normalizer": "keyword_lowercase_normalizer", "type": "keyword"},
                "pmid": {"normalizer": "keyword_lowercase_normalizer", "type": "keyword"},
                "species": {"normalizer": "keyword_lowercase_normalizer", "type": "keyword"},
                "tissue": {"normalizer": "keyword_lowercase_normalizer", "type": "keyword"},
                "uberon": {"normalizer": "keyword_lowercase_normalizer", "type": "keyword"},
                "company": {"normalizer": "keyword_lowercase_normalizer", "type": "keyword"},
            }
        }
    }
    return mapping
