# -*- coding: utf-8 -*-
from biothings.web.api.es.query_builder import ESQueryBuilder
from biothings.utils.common import is_int
import json
import re
#import logging

def safe_genome_pos(s):
    '''
        safe_genome_pos(1000) = 1000
        safe_genome_pos('1000') = 1000
        safe_genome_pos('10,000') = 100000
     '''
    if isinstance(s, int):
        return s
    elif isinstance(s, str):
        return int(s.replace(',', ''))
    else:
        raise ValueError('invalid type "%s" for "save_genome_pos"' % type(s))

class ESQueryBuilder(ESQueryBuilder):
    def _POST_single_query(self, term, scopes=None):
        if not term:
            return self.queries.match({"non_exist_field":""})

        if len(scopes) == 1 and '*' not in scopes[0]:
            q = self.queries.match({scopes[0]:{"query": "{}".format(term), "operator": "and"}})
        else:
            q = self.queries.multi_match({"query": "{}".format(term), "fields": scopes, "operator": "and"})

        q["query"] = self.add_query_filters(q["query"])
        q["query"] = self.add_species_custom_filters_score(q["query"])
        return q

    def _POST_query(self, qs, scopes):
        _q = []
        INT_FIELDS = set(['entrezgene', 'retired'])
        
        if not scopes:
            scopes = self.default_scopes

        for term in qs:
            #logging.debug("Term: {}".format(term))
            if is_int(term) and set(scopes).intersection(INT_FIELDS):
                _q.extend(['{}', json.dumps(self._POST_single_query(term, scopes=
                    list(set(scopes).intersection(INT_FIELDS))))])
            elif not is_int(term) and set(scopes).difference(INT_FIELDS):
                _q.extend(['{}', json.dumps(self._POST_single_query(term, scopes=
                    list(set(scopes).difference(INT_FIELDS))))])
            else:
                _q.extend(['{}', json.dumps(self._POST_single_query(term=None))])
        return self._return_query_kwargs({'body': '\n'.join(_q)})

    def _query_POST_query(self, qs, scopes):
        return self._POST_query(qs, scopes)

    def _annotation_POST_query(self, bids):
        return self._POST_query(qs=bids, scopes=['entrezgene', 'retired', 'ensembl.gene'])

    def get_query_filters(self):
        # BioThings filters
        _filters = self._get_query_filters()

        #logging.debug("_filters: {}".format(_filters))

        # mygene filters
        if 'all' not in self.options.species:
            if len(self.options.species) == 1:
                _filters.append({"term":{"taxid":self.options.species[0]}})
            else:
                _filters.append({"terms":{"taxid":self.options.species}})
        if self.options.entrezonly:
            _filters.append({"exists":{"field":"entrezgene"}})
        if self.options.ensemblonly:
            _filters.append({"exists":{"field":"ensembl.gene"}})
        if self.options.exists:
            for _filter in self.options.exists:
                _filters.append({"exists":{"field":_filter}})
        if self.options.missing:
            for _filter in self.options.missing:
                _filters.append({"missing":{"field":_filter}})    
        if _filters:
            if len(_filters) == 1:
                _filters = _filters[0]
            else:
                _filters = {"and": _filters}

        return _filters            

    def _extra_query_types(self, q):
        ''' Overridden to add extra queries for mygene query GET endpoint '''
        if self._is_genomic_interval_query(q):
            return self.genomic_interval_query(**self._is_genomic_interval_query(q))
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

    def _is_genomic_interval_query(self, query):
        '''Check if the input query string matches interval search regex,
           if yes, return a dictionary with three key-value pairs:
              chr
              gstart
              gend
            , otherwise, return None.
        '''
        pattern = r'chr(?P<chrom>\w+):(?P<gstart>[0-9,]+)-(?P<gend>[0-9,]+)'
        if query:
            mat = re.search(pattern, query)
            if mat:
                d = mat.groupdict()
                if query.startswith('hg19.'):
                    # support hg19 for human (default is hg38)
                    d['assembly'] = 'hg19'
                if query.startswith('mm9.'):
                    # support mm9 for mouse (default is mm10)
                    d['assembly'] = 'mm9'

                return d

    def _genomic_interval_query(self, chrom, gstart, gend, assembly=None):
        '''By default if assembly is None, the lastest assembly is used.
           for some species (e.g. human) we support multiple assemblies,
           exact assembly is passed as well.
        '''
        gstart = safe_genome_pos(gstart)
        gend = safe_genome_pos(gend)
        if chrom.lower().startswith('chr'):
            chrom = chrom[3:]

        genomic_pos_field = "genomic_pos"
        if assembly:
            if assembly == 'hg19':
                genomic_pos_field = "genomic_pos_hg19"
            if assembly == 'mm9':
                genomic_pos_field = "genomic_pos_mm9"

        _query = {
            "nested": {
                "path": genomic_pos_field,
                "query": {
                    "bool": {
                        "must": [
                            {"term": {
                                genomic_pos_field + ".chr": chrom.lower()}},
                            {"range": {
                                genomic_pos_field + ".start": {"lte": gend}}},
                            {"range": {
                                genomic_pos_field + ".end": {"gte": gstart}}}
                        ]
                    }
                }
            }
        }
        return _query

    def add_extra_filters(self, q):
        ''' Override to add mygene specific query structure '''
        _q = {'query': self.add_species_custom_filters_score(q)}
        _q = self.add_facet_filters(_q)
        return _q

    def genomic_interval_query(self, chrom, gstart, gend, assembly=None):
        return self._genomic_interval_query(chrom, gstart, gend, assembly)

    def raw_string_query(self, q):
        return self._raw_string_query(q)

    def wildcard_query(self, q):
        return self._wildcard_query(q)

    def dis_max_query(self, q):
        return self._dis_max_query(q)

    def _default_query(self, q):
        return self.dis_max_query(q)
    
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

    def add_species_custom_filters_score(self, _query):
        _query = {
            "function_score": {
                "query": _query,
                "functions": [
                    # downgrade "pseudogene" matches
                    {
                        "filter": {"term": {"name": "pseudogene"}},
                        "weight": "0.5"
                    },
                    {
                        "filter": {"term": {"taxid": 9606}},
                        "weight": "1.55"
                    },
                    {
                        "filter": {"term": {"taxid": 10090}},
                        "weight": "1.3"
                    },
                    {
                        "filter": {"term": {"taxid": 10116}},
                        "weight": "1.1"
                    },
                ],
                "score_mode": "first"
            }
        }
        return _query

    def add_facet_filters(self, _query):
        """To add filters (e.g. taxid) to restrict returned hits,
            but does not change the scope for facet counts.
        """
        _filters = []
        # species_facet_filter
        if self.options.species_facet_filter:
            if len(self.options.species_facet_filter) == 1:
                _filters.append({
                    "term": {"taxid": self.options.species_facet_filter[0]}
                })
            else:
                _filters.append({
                    "terms": {"taxid": self.options.species_facet_filter}
                })
        if _filters:
            if len(_filters) == 1:
                _filters = _filters[0]
            else:
                # concatenate multiple filters with "and" filter
                _filters = {"and": _filters}

            # this will not change facet counts
            _query["filter"] = _filters

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
