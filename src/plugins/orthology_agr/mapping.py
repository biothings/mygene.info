def get_customized_mapping(cls):
    mapping={
    "agr": {
        "properties": {
            "orthologs": {
                "properties": {
                    "geneid": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "symbol": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "taxid": {
                        "type": "integer"
                    },
                    "algorithmsmatch": {
                        "type": "integer"
                    },
                    "outofalgorithms": {
                        "type": "integer"
                    },
                    "isbestscore": {
                        "type": "boolean"
                    },
                    "isbestrevscore": {
                        "type": "boolean"
                    }
                }
            }
        }
    }
}
    return mapping;