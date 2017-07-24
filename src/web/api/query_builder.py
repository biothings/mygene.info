# -*- coding: utf-8 -*-
from biothings.www.api.es.query_builder import ESQueryBuilder
from biothings.utils.common import is_int
import json

class ESQueryBuilder(ESQueryBuilder):
    def _extra_query_types(self, q):
        ''' Overridden to add extra queries for mygene query GET endpoint '''
        if self._is_raw_string_query(q):
            return self.raw_string_query(q)
        elif self._is_wildcard_query(q):
            return self.wildcard_query(q)
        return None

    def _is_wildcard_query(self, query):
        ''' Return True if input query is a wildcard query. '''
        return query.find('*') != -1 or query.find('?') != -1

    def _is_raw_string_query(self, query):
        '''Return True if input query is a wildchar/fielded/boolean query.'''
        for v in [':', '~', ' AND ', ' OR ', 'NOT ']:
            if query.find(v) != -1:
                return True
        if query.startswith('"') and query.endswith('"'):
            return True
        return False

    def raw_string_query(self, q):
        return self.queries.raw_query(self._raw_string_query(q))

    def wildcard_query(self, q):
        return self.queries.raw_query(self._wildcard_query(q))

    def dis_max_query(self, q):
        return self.queries.raw_query(self._dis_max_query(q))

    def _default_query(self, q):
        return self.queries.raw_query(self.dis_max_query(q))
    
    def _raw_string_query(self, q):
        _query = {
            "query_string": {
                "query": "%(q)s",
                # "analyzer": "string_lowercase",
                "default_operator": "AND",
                "auto_generate_phrase_queries": True
            }
        }
        _query = json.dumps(_query)
        try:
            _query = json.loads(_query % {'q': q.replace('"', '\\"')})
        except ValueError:
            raise ValueError("invalid query term.")
        return _query

    def _dis_max_query(self, q):
        # remove '"' and '\' from q, they will break json decoder.
        q = q.replace('"', '').replace('\\', '')
        _query = {
            "dis_max": {
                "tie_breaker": 0,
                "boost": 1,
                "queries": [
                    {
                        "function_score": {
                            "query": {
                                "match": {
                                    "symbol": {
                                        "query": "%(q)s",
                                        "analyzer": "whitespace_lowercase"
                                    }
                                },
                            },
                            "weight": 5
                        }
                    },
                    {
                        "function_score": {
                            "query": {
                                # This makes phrase match of "cyclin-dependent
                                # kinase 2" appears first
                                "match_phrase": {"name": "%(q)s"},
                            },
                            "weight": 4

                        }
                    },
                    {
                        "function_score": {
                            "query": {
                                "match": {
                                    "name": {
                                        "query": "%(q)s",
                                        "operator": "and",
                                        "analyzer": "whitespace_lowercase"
                                    }
                                },
                            },
                            "weight": 3
                        }
                    },
                    {
                        "function_score": {
                            "query": {
                                "match": {
                                    "unigene": {
                                        "query": "%(q)s",
                                        "analyzer": "string_lowercase"
                                    }
                                }
                            },
                            "weight": 1.1
                        }
                    },
                    {
                        "function_score": {
                            "query": {
                                "multi_match": {
                                    "query": "%(q)s",
                                    "fields": [
                                        'refseq.*', 'accession.*'
                                    ],
                                    "operator": "or"
                                }
                            },
                            "weight": 1.1
                        }
                    },
                    {
                        "function_score": {
                            "query": {
                                "match": {
                                    "go": {
                                        "query": "%(q)s",
                                        "analyzer": "string_lowercase"
                                    }
                                }
                            },
                            "weight": 1.1
                        }
                    },
                    # {
                    # "custom_boost_factor": {
                    #     "query" : {
                    #         "match" : { "_all" : {
                    #                     "query": "%(q)s",
                    #                     "analyzer": "whitespace_lowercase"
                    #             }
                    #         },
                    #     },
                    #     "boost_factor": 1
                    # }
                    # },
                    {
                        "function_score": {
                            "query": {
                                "query_string": {
                                    "query": "%(q)s",
                                    "default_operator": "AND",
                                    "auto_generate_phrase_queries": True
                                },
                            },
                            "weight": 1
                        }
                    },

                ]
            }
        }
        _query = json.dumps(_query)
        _query = json.loads(_query % {'q': q})

        if is_int(q):
            _query['dis_max']['queries'] = []
            _query['dis_max']['queries'].insert(
                0,
                {
                    "function_score": {
                        "query": {
                            "term": {"entrezgene": int(q)},
                        },
                        "weight": 8
                    }
                }
            )

        return _query

    def wildcard_query(self, q):
        '''q should contains either * or ?, but not the first character.'''
        _query = {
            "dis_max": {
                "tie_breaker": 0,
                "boost": 1,
                "queries": [
                    {
                        "function_score": {
                            "query": {
                                "wildcard": {
                                    "symbol": {
                                        "value": "%(q)s",
                                        # "weight": 5.0,
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
                                        "value": "%(q)s",
                                        # "weight": 1.1,
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
                                        "value": "%(q)s",
                                        # "weight": 0.5,
                                    }
                                },
                            }
                        }
                    },

                ]
            }
        }
        _query = json.dumps(_query)
        try:
            _query = json.loads(_query % {'q': q.lower()})
        except ValueError:
            raise ValueError("invalid query term.")

        return _query
