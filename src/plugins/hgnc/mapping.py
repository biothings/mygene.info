def get_customized_mapping(cls):
    # same as `alias` and `symbol` in entrez gene_upload.py
    mapping = {
        "prev_symbol": {
            "type": "keyword",
            "normalizer": "keyword_lowercase_normalizer",
            "copy_to": "all",
        }
    }
    return mapping
