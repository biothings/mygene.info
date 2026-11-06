"""
    Queries not defined by es-dsl.
"""

from biothings.utils.common import is_int

# Fixed scores instead of BM25: BM25's IDF is computed per field, so symbol
# and prev_symbol scores wouldn't be comparable. Symbol hits score
# 8 * 12 = 96, within the range BM25 used to give them. prev_symbol hits
# score 0.68 of that, so a human former symbol ranks below current symbols
# in build.py's common species and above those in all other species.
# Used by the default query below and by POST lookups in build.py.
SYMBOL_WEIGHTS = {"symbol": 8, "prev_symbol": 5.44}


def symbol_tier(field, match):
    """Wrap a match query on field so that a hit scores 12 * SYMBOL_WEIGHTS[field]."""
    return {
        "function_score": {
            "query": {"constant_score": {"filter": match, "boost": 12}},
            "weight": SYMBOL_WEIGHTS[field],
        }
    }


def symbol_queries(q):

    if len(q.split()) > 1:
        # a hit on one of several terms is not an exact match, keep BM25
        return [
            {
                "function_score": {
                    "query": {
                        "match": {
                            "symbol": {"query": q, "analyzer": "whitespace_lowercase"}
                        },
                    },
                    "weight": 8,
                }
            },
        ]

    # prev_symbol holds former official symbols, e.g. PARK2 for PRKN
    return [
        symbol_tier(field, {"match": {field: {"query": q, "analyzer": "whitespace_lowercase"}}})
        for field in SYMBOL_WEIGHTS
    ]


def dismax(q):

    _query = {
        "tie_breaker": 0,
        "boost": 1,
        "queries": [
            *symbol_queries(q),
            {
                "function_score": {
                    "query": {
                        # This makes phrase match of "cyclin-dependent
                        # kinase 2" appears first
                        "match_phrase": {"name": q},
                    },
                    "weight": 4,
                }
            },
            {
                "function_score": {
                    "query": {
                        "match": {
                            "name": {
                                "query": q,
                                "operator": "and",
                                "analyzer": "whitespace_lowercase",
                            }
                        },
                    },
                    "weight": 3,
                }
            },
            {
                "function_score": {
                    "query": {
                        "match": {
                            "unigene": {"query": q, "analyzer": "string_lowercase"}
                        }
                    },
                    "weight": 1.1,
                }
            },
            {
                "function_score": {
                    "query": {
                        "multi_match": {
                            "query": q,
                            "fields": [
                                "refseq.rna",
                                "refseq.protein",
                                "accession.rna",
                                "accession.protein",
                            ],
                            "operator": "or",
                        }
                    },
                    "weight": 1.1,
                }
            },
            {
                "function_score": {
                    "query": {
                        "match": {"go": {"query": q, "analyzer": "string_lowercase"}}
                    },
                    "weight": 1.1,
                }
            },
            {
                "function_score": {
                    "query": {
                        "query_string": {"query": q, "default_operator": "AND"},
                    },
                    "weight": 1,
                }
            },
        ],
    }

    if is_int(q):
        _query["queries"] = [
            {
                "function_score": {
                    "query": {
                        "term": {"entrezgene": int(q)},
                    },
                    "weight": 8,
                }
            }
        ]

    return {"query": {"dis_max": _query}}


def wildcard(q):
    """q should contains either * or ?, but not the first character."""

    _query = {
        "tie_breaker": 0,
        "boost": 1,
        "queries": [
            {
                "function_score": {
                    "query": {
                        "wildcard": {
                            "symbol": {
                                "value": q.lower(),
                            }
                        },
                    },
                }
            },
            {
                "function_score": {
                    "query": {
                        "wildcard": {
                            "name": {
                                "value": q.lower(),
                            }
                        },
                    }
                }
            },
            {
                "function_score": {
                    "query": {
                        "wildcard": {
                            "summary": {
                                "value": q.lower(),
                            }
                        },
                    }
                }
            },
        ],
    }

    return {"query": {"dis_max": _query}}


def safe_genome_pos(s):
    """
    safe_genome_pos(1000) = 1000
    safe_genome_pos('1000') = 1000
    safe_genome_pos('10,000') = 100000
    """
    if isinstance(s, int):
        return s
    elif isinstance(s, str):
        return int(s.replace(",", ""))
    else:
        raise ValueError('invalid type "%s" for "save_genome_pos"' % type(s))


def interval(chrom, gstart, gend, assembly=None):
    """By default if assembly is None, the lastest assembly is used.
    for some species (e.g. human) we support multiple assemblies,
    exact assembly is passed as well.
    """
    gstart = safe_genome_pos(gstart)
    gend = safe_genome_pos(gend)
    if chrom.lower().startswith("chr"):
        chrom = chrom[3:]

    genomic_pos_field = "genomic_pos"
    if assembly:
        if assembly == "hg19":
            genomic_pos_field = "genomic_pos_hg19"
        if assembly == "mm9":
            genomic_pos_field = "genomic_pos_mm9"

    _query = {
        "nested": {
            "path": genomic_pos_field,
            "query": {
                "bool": {
                    "must": [
                        {"term": {genomic_pos_field + ".chr": chrom.lower()}},
                        {"range": {genomic_pos_field + ".start": {"lte": gend}}},
                        {"range": {genomic_pos_field + ".end": {"gte": gstart}}},
                    ]
                }
            },
        }
    }
    return dict(query=_query)
