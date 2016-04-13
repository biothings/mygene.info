"""Module to query ES indexes"""

#http://www.elasticsearch.org/guide/reference/query-dsl/custom-filters-score-query.html
#http://www.elasticsearch.org/guide/reference/query-dsl/custom-score-query.html
#http://www.elasticsearch.org/guide/reference/query-dsl/custom-boost-factor-query.html
#http://www.elasticsearch.org/guide/reference/query-dsl/boosting-query.html
import sys

import json
import re
import time
import copy
import requests
import logging

from config import (ES_HOST, ES_INDEX_NAME_TIER1, ES_INDEX_NAME,
                    ES_DOC_TYPE)
from biothings.utils.common import (ask, is_int, is_str, is_seq, timesofar, dotdict)
from biothings.utils.dotfield import parse_dot_fields, compose_dot_fields_by_fields as compose_dot_fields
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
#from src.utils.dotfield import compose_dot_fields_by_fields as compose_dot_fields



GENOME_ASSEMBLY = {
    "human": "hg38",
    "mouse": "mm10",
    "rat": "rn4",
    "fruitfly": "dm3",
    "nematode": "ce10",
    "zebrafish": "zv9",
    "frog": "xenTro3",
    "pig": "susScr2"
}

TAXONOMY = {
    "human": 9606,
    "mouse": 10090,
    "rat": 10116,
    "fruitfly": 7227,
    "nematode": 6239,
    "zebrafish": 7955,
    "thale-cress": 3702,
    "frog": 8364,
    "pig": 9823
}


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



from biothings.www.api.es import ESQuery, QueryError

class ESQuery(ESQuery):
    def __init__(self):
        super( ESQuery, self ).__init__()
        self._default_fields = ['name', 'symbol', 'taxid', 'entrezgene']
        self._default_species = [9606, 10090, 10116] # human, mouse, rat
        self._tier_1_species = set(TAXONOMY.values())

    def _search(self, q, species='all', scroll_options={}):
        self._set_index(species)
        # body = '{"query" : {"term" : { "_all" : ' + q + ' }}}'
        #logging.error("in search q: %s -- index: %s -- doc_type: %s" % (json.dumps(q),self._index,self._doc_type))
        res = self._es.search(index=self._index, doc_type=self._doc_type,
                               body=q, **scroll_options)
        #logging.error("in search: %s" % res)
        self._index = ES_INDEX_NAME # reset self._index
        return res

    def _msearch(self, q, species='all'):
        self._set_index(species)
        # path = make_path(self._index, self._doc_type, '_msearch')
        res = self._es.msearch(index=self._index, doc_type=self._doc_type,
                                body=q)
        self._index = ES_INDEX_NAME     # reset self._index
        return res

    def _set_index(self, species):
        '''set proper index for given species parameter.'''
        if species == 'all' or len(set(species)-self._tier_1_species) > 0:
            self._index = ES_INDEX_NAME
        else:
            self._index = ES_INDEX_NAME_TIER1

    def _get_genedoc(self, hit, dotfield=False):
        doc = hit.get('_source', hit.get('fields', {}))
        doc.setdefault('_id', hit['_id'])
        if '_version' in hit:
            doc.setdefault('_version', hit['_version'])
        if not dotfield:
            doc = parse_dot_fields(doc)
        return doc

    def _get_genedoc_2(self, hit, dotfield=False, fields=None):
        """
        use ES _source to support fields/filter argument,
        by default ES response is not dotted.
        """
        doc = hit.get('_source', hit.get('fields', {}))
        doc.setdefault('_id', hit['_id'])
        if '_version' in hit:
            doc.setdefault('_version', hit['_version'])
        if dotfield and fields:
            doc = compose_dot_fields(doc, fields)
        return doc

    def _cleaned_res(self, res, empty=[], error={'error': True}, single_hit=False, dotfield=False):
        '''res is the dictionary returned from a query.'''
        if 'error' in res:
            return error

        hits = res['hits']
        total = hits['total']
        if total == 0:
            return empty
        elif total == 1 and single_hit:
            return self._get_genedoc(hits['hits'][0], dotfield=dotfield)
        else:
            return [self._get_genedoc(hit, dotfield=dotfield) for hit in hits['hits']]

    def _cleaned_res_2(self, res, empty=[], error={'error': True},
                       single_hit=False, dotfield=False, fields=None):
        if 'error' in res:
            return error

        hits = res['hits']
        total = hits['total']
        if total == 0:
            return empty
        elif total == 1 and single_hit:
            return self._get_genedoc_2(hits['hits'][0],
                                       dotfield=dotfield, fields=fields)
        else:
            return [self._get_genedoc_2(hit,
                                        dotfield=dotfield, fields=fields)
                    for hit in hits['hits']]

    def _cleaned_res_3(self, res, dotfield=False, fields=None):
        ''' res is the dictionary returned from a query.
            do some reformating of raw ES results before returning.

            This method is used for self.query method.
        '''
        if 'aggregations' in res:
            # need to normalize back to what "facets" used to return
            # (mostly key renaming + total computation)
            res["facets"] = res.pop("aggregations")
            for facet in res["facets"]:
                # restuls always coming from terms aggregations
                res["facets"][facet]["_type"] = "terms"
                res["facets"][facet]["terms"] = res["facets"][facet].pop("buckets")
                res["facets"][facet]["other"] = res["facets"][facet].pop("sum_other_doc_count")
                res["facets"][facet]["missing"] = res["facets"][facet].pop("doc_count_error_upper_bound")
                count = 0
                for term in res["facets"][facet]["terms"]:
                    # modif in-place
                    term["count"] = term.pop("doc_count")
                    term["term"] = term.pop("key")
                    count += term["count"]
                res["facets"][facet]["total"] = count

        _res = res['hits']
        for attr in ['took', 'facets', '_scroll_id']:
            if attr in res:
                _res[attr] = res[attr]
        _res['hits'] = [self._get_genedoc_2(hit,dotfield,fields) for hit in _res['hits']]
        return _res

    # keepit (?)
    def _cleaned_species(self, species, default_to_none=False):
        '''return a cleaned species parameter.
           should be either "all" or a list of taxids/species_names, or a single taxid/species_name.
           returned species is always a list of taxids (even when only one species)
        '''
        if species is None:
            #set to default_species
            return None if default_to_none else self._default_species
        if isinstance(species, int):
            return [species]

        if is_str(species):
            if species.lower() == 'all':
                #if self.species == 'all': do not apply species filter, all species is included.
                return species.lower()
            else:
                species = [s.strip().lower() for s in species.split(',')]

        if not is_seq(species):
            raise ValueError('"species" parameter must be a string, integer or a list/tuple, not "{}".'.format(type(species)))

        _species = []
        for s in species:
            if is_int(s):
                _species.append(int(s))
            elif s in TAXONOMY:
                _species.append(TAXONOMY[s])
        return _species

    # keepit (?)
    def _parse_interval_query(self, query):
        '''Check if the input query string matches interval search regex,
           if yes, return a dictionary with three key-value pairs:
              chr
              gstart
              gend
            , otherwise, return None.
        '''
        pattern = r'chr(?P<chr>\w+):(?P<gstart>[0-9,]+)-(?P<gend>[0-9,]+)'
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

    # keepit (?)
    def _is_wildcard_query(self, query):
        '''Return True if input query is a wildcard query.'''
        return query.find('*') != -1 or query.find('?') != -1

    # keepit (?)
    def _is_raw_string_query(self, query):
        '''Return True if input query is a wildchar/fielded/boolean query.'''
        for v in [':', '~', ' AND ', ' OR ', 'NOT ']:
            if query.find(v) != -1:
                return True
        if query.startswith('"') and query.endswith('"'):
            return True
        return False

    # keepit but refactor
    def _get_cleaned_query_options(self, kwargs):
        """common helper for processing fields, kwargs and other options passed to ESQueryBuilder."""
        #TODO: kwargs is used to fill options dict, some keys are popped, not all, then
        # options.kwargs = kwargs. from caller perspective, kwargs changes, not the same in options.kwargs, which is weird.
        options = dotdict()
        options.raw = kwargs.pop('raw', False)
        options.rawquery = kwargs.pop('rawquery', False)
        #if dofield is false, returned fields contains dot notation will be restored as an object.
        options.dotfield = kwargs.pop('dotfield', False) not in [False, 'false']
        options.fetch_all = kwargs.pop('fetch_all', False)
        scopes = kwargs.pop('scopes', None)
        if scopes:
            options.scopes = self._cleaned_scopes(scopes)
        kwargs["fields"] = self._cleaned_fields(kwargs.get("fields"))

        #if no dotfield in "fields", set dotfield always be True, i.e., no need to parse dotfield
        if not options.dotfield:
            _found_dotfield = False
            if kwargs.get('fields'):
                for _f in kwargs['fields']:
                    if _f.find('.') != -1:
                        _found_dotfield = True
                        break
            if not _found_dotfield:
                options.dotfield = True

        # TODO: something is wrong here...
        #options = super( ESQuery, self )._get_cleaned_query_options(kwargs)

        #this species parameter is added to the query, thus will change facet counts.
        kwargs['species'] = self._cleaned_species(kwargs.get('species', None))
        include_tax_tree = kwargs.pop('include_tax_tree', False)
        if include_tax_tree:
            headers = {'content-type': 'application/x-www-form-urlencoded',
                      'user-agent': "Python-requests_mygene.info/%s (gzip)" % requests.__version__}
            res = requests.post('http://s.biothings.io/v1/species?ids=' + 
                                ','.join(['{}'.format(sid) for sid in kwargs['species']]) +
                                '&expand_species=true', headers=headers)
            if res.status_code == requests.codes.ok:
                kwargs['species'] = res.json()

        #this parameter is to add species filter without changing facet counts.
        kwargs['species_facet_filter'] = self._cleaned_species(kwargs.get('species_facet_filter', None),
                                                               default_to_none=True)

        options.kwargs = kwargs
        return options

    def get_gene(self, geneid, fields='all', **kwargs):
        kwargs['fields'] = self._cleaned_fields(fields)
        raw = kwargs.pop('raw', False)
        try:
            res = self._es.get(index=self._index, doc_type=self._doc_type,
                                id=geneid, **kwargs)
        except NotFoundError:
            return None
        return res if raw else self._get_genedoc(res)

    def mget_gene(self, geneid_list, fields=None, **kwargs):
        kwargs['fields'] = self._cleaned_fields(fields)
        raw = kwargs.pop('raw', False)
        res = self._es.mget(geneid_list, self._index, self._doc_type, **kwargs)
        return res if raw else [self._get_genedoc(doc) for doc in res]

    def get_gene2(self, geneid, fields='all', **kwargs):
        '''for /gene/<geneid>'''
        kwargs["fields"] = fields
        options = self._get_cleaned_query_options(kwargs)
        qbdr = ESQueryBuilder(**options.kwargs)
        _q = qbdr.build_id_query(geneid, options.scopes)
        if options.rawquery:
            return _q
        res = self._search(_q, species=options.kwargs['species'])
        if not options.raw:
            res = self._cleaned_res_2(res, empty=None, single_hit=True,
                                      dotfield=options.dotfield,
                                      fields=options.kwargs['fields'])
        return res

    def mget_gene2(self, geneid_list, fields=None, **kwargs):
        '''for /query post request'''
        kwargs["fields"] = fields
        options = self._get_cleaned_query_options(kwargs)
        qbdr = ESQueryBuilder(**options.kwargs)
        try:
            _q = qbdr.build_multiple_id_query(geneid_list, options.scopes)
        except QueryError as err:
            return {'success': False,
                    'error': err.message}
        if options.rawquery:
            return _q
        res = self._msearch(_q, kwargs['species'])['responses']
        if options.raw:
            return res

        assert len(res) == len(geneid_list)
        _res = []
        for i in range(len(res)):
            hits = res[i]
            qterm = geneid_list[i]
            hits = self._cleaned_res_2(hits, empty=[], single_hit=False,
                                       dotfield=options.dotfield,
                                       fields=options.kwargs['fields'])
            if len(hits) == 0:
                _res.append({u'query': qterm,
                             u'notfound': True})
            elif 'error' in hits:
                _res.append({u'query': qterm,
                             u'error': True})
            else:
                for hit in hits:
                    hit[u'query'] = qterm
                    _res.append(hit)
        return _res

    def query(self, q, fields=None, **kwargs):
        '''for /query?q=<query>'''
        kwargs["fields"] = fields
        options = self._get_cleaned_query_options(kwargs)
        qbdr = ESQueryBuilder(**options.kwargs)
        q = re.sub(u'[\t\n\x0b\x0c\r\x00]+', ' ', q)
        q = q.strip()
        _q = None
        scroll_options = {}
        if options.fetch_all:
            # TODO: ES2 compatible ?
            scroll_options.update({'search_type': 'scan', 'size': self._scroll_size, 'scroll': self._scroll_time})
        # Check if special interval query pattern exists
        interval_query = self._parse_interval_query(q)
        try:
            if interval_query:
                # should also passing a "taxid" along with interval.
                if qbdr.species != 'all':
                    qbdr.species = [qbdr.species[0]]
                    _q = qbdr.build_genomic_pos_query(**interval_query)
                else:
                    return {'success': False,
                            'error': 'genomic interval query cannot be combined with "species=all" parameter. Specify a single species.'}

            # Check if fielded/boolean query, excluding special goid query
            # raw_string_query should be checked ahead of wildcard query, as raw_string may contain wildcard as well
            # e.g., a query "symbol:CDK?", should be treated as raw_string_query.
            elif self._is_raw_string_query(q) and not q.lower().startswith('go:'):
                _q = qbdr.build(q, mode=3)   # raw string query
            elif self._is_wildcard_query(q):
                _q = qbdr.build(q, mode=2)   # wildcard query
            else:
                # normal text query
                _q = qbdr.build(q, mode=1)
        except QueryError as e:
            msg = str(e)
            return {'success': False,
                    'error': msg}

        if _q:
            if options.rawquery:
                return _q

            try:
                res = self._search(_q, species=kwargs['species'], scroll_options=scroll_options)
            except Exception as e:
                # TODO: critical/sensitive data in exception message ? 
                msg = str(e.info)
                return {'success': False, 'error': msg}

            if not options.raw:
                res = self._cleaned_res_3(res,options.get("dotfield"),kwargs.get("fields"))
                ###res = self._cleaned_res2(res,options)
                #_res = res['hits']
                #_res['took'] = res['took']
                #if "facets" in res:
                #    _res['facets'] = res['facets']
                #for v in _res['hits']:
                #    del v['_type']
                #    del v['_index']
                #    for attr in ['fields', '_source']:
                #        if attr in v:
                #            v.update(v[attr])
                #            del v[attr]
                #            break
                #    if not options.dotfield:
                #        parse_dot_fields(v)
                #res = _res
        else:
            res = {'success': False,
                   'error': "Invalid query. Please check parameters."}

        return res

    def scroll(self, scroll_id, fields=None, **kwargs):
        kwargs["fields"] = fields
        options = self._get_cleaned_query_options(kwargs)
        r = self._es.scroll(scroll_id, scroll=self._scroll_time)
        scroll_id = r.get('_scroll_id')
        if scroll_id is None or not r['hits']['hits']:
            return {'success': False, 'error': 'No results to return.'}
        else:
            if not options.raw:
                res = self._cleaned_res_3(r)
        #res.update({'_scroll_id': scroll_id})
        if r['_shards']['failed']:
            res.update({'_warning': 'Scroll request has failed on {} shards out of {}.'.format(r['_shards']['failed'], r['_shards']['total'])})
        return res

    # keepit
    def doc_feeder(self, step=1000, s=None, e=None, inbatch=False, query=None, **kwargs):
        '''deprecated! A iterator for returning docs in a ES index with batch query.
           additional filter query can be passed via "query", e.g.,
           doc_feeder(query='taxid:9606'}})
           other parameters can be passed via "**kwargs":
                fields, from, size etc.
        '''
        if query:
            q = StringQuery(query)
        else:
            q = MatchAllQuery()
        raw_res = None

        cnt = 0
        t0 = time.time()
        while 1:
            t1 = time.time()
            if raw_res is None:
                raw_res = self._es.search_raw(q, self._index, self._doc_type,
                                               start=s, size=step, scan=True,
                                               scroll='5m', **kwargs)
                n = raw_res['hits']['total']
                print('Retrieving %d documents from index "%s/%s".' % (n, self._index, self._doc_type))
            else:
                raw_res = self._es.search_scroll(raw_res._scroll_id, scroll='5m')
            hits_cnt = len(raw_res['hits']['hits'])
            if hits_cnt == 0:
                break
            else:

                print("Processing %d-%d documents..." % (cnt+1, cnt + hits_cnt),)
                res = self._cleaned_res(raw_res)
                if inbatch:
                    yield res
                else:
                    for hit in res:
                        yield hit
                cnt += hits_cnt
                print('Done.[%.1f%%,%s]' % (cnt*100./n, timesofar(t1)))
                if e and cnt > e:
                    break

        print('Finished.[total docs: %s, total time: %s]' % (cnt, timesofar(t0)))

    # keepit
    def metadata(self, raw=False):
        '''return metadata about the index.'''
        mapping = self._es.indices.get_mapping(self._index, self._doc_type)
        if raw:
            return mapping

        def get_fields(properties):
            for k, v in list(properties.items()):
                if 'properties' in v:
                    for f in get_fields(v['properties']):
                        yield f
                else:
                    if v.get('index', None) == 'no':
                        continue
                    f = v.get('index_name', k)
                    yield f
        mapping = list(mapping.values())[0]['mappings']
        #field_set = set(get_fields(mapping[self._doc_type]['properties']))
        metadata = {
            #'available_fields': sorted(field_set)
            # TODO: http://mygene.info as config
            'available_fields': 'http://mygene.info/metadata/fields'
        }
        if '_meta' in mapping[self._doc_type]:
            metadata.update(mapping[self._doc_type]['_meta'])
        metadata['genome_assembly'] = GENOME_ASSEMBLY
        metadata['taxonomy'] = TAXONOMY
        return metadata


class ESQueryBuilder():
    def __init__(self, **query_options):
        """You can pass these options:
            fields     default ['name', 'symbol', 'taxid', 'entrezgene']
            from       default 0
            size       default 10
            sort       e.g. sort='entrezgene,-symbol'
            explain    true or false
            facets     a field or a list of fields, default None

            species
            species_facet_filter
            entrezonly  default false
            ensemblonly default false
            userfilter  optional, provide the name of a saved user filter (in "userfilters" index)
            exists      optional, passing field, comma-separated fields, returned
                                  genes must have given field(s).
            missing     optional, passing field, comma-separated fields, returned
                                  genes must have NO given field(s).

        """
        self.options = query_options
        self.species = self.options.pop('species', 'all')   # species should be either 'all' or a list of taxids.
        self.species_facet_filter = self.options.pop('species_facet_filter', None)
        self.entrezonly = self.options.pop('entrezonly', False)
        self.ensemblonly = self.options.pop('ensemblonly', False)
        # userfilter
        userfilter = self.options.pop('userfilter', None)
        self.userfilter = userfilter.split(',') if userfilter else None
        # exist filter
        existsfilter = self.options.pop('exists', None)
        self.existsfilter = existsfilter.split(',') if existsfilter else None
        # missing filter
        missingfilter = self.options.pop('missing', None)
        self.missingfilter = missingfilter.split(',') if missingfilter else None

        self._parse_sort_option(self.options)
        self._parse_facets_option(self.options)
        self._allowed_options = ['fields', 'start', 'from', 'size',
                                 'sort', 'explain', 'version', 'aggs','dotfield']
        for key in set(self.options) - set(self._allowed_options):
            del self.options[key]
        # convert "fields" option to "_source"
        # use "_source" instead of "fields" for ES v1.x and up
        if 'fields' in self.options and self.options['fields'] is not None:
            self.options['_source'] = self.options['fields']
            del self.options['fields']

        # this is a fake query to make sure to return empty hits
        self._nohits_query = {
            "match": {
                'non_exist_field': ''
            }
        }

    # keepit (?)
    def dis_max_query(self, q):
        #remove '"' and '\' from q, they will break json decoder.
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
                                #This makes phrase match of "cyclin-dependent kinase 2" appears first
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
                    #                         "query": "%(q)s",
                    #                         "analyzer": "whitespace_lowercase"
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


    # keepit (?)
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
            raise QueryError("invalid query term.")

        return _query

    # keepit (?)
    def string_query(self, q):
        _query = {
            "query_string": {
                "query": "%(q)s",
                "analyzer": "string_lowercase",
                "default_operator": "AND",
                "auto_generate_phrase_queries": True
            }
        }
        _query = json.dumps(_query)
        q = "symbol:%(q)s OR name:%(q)s OR %(q)s" % {'q': q}
        _query = json.loads(_query % {'q': q})
        return _query

    # keepit (?)
    def raw_string_query(self, q):
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
            raise QueryError("invalid query term.")
        return _query

    # keepit (?)
    def add_species_filter(self, _query):
        """deprecated! replaced by  """
        if self.species == 'all':
            #do not apply species filter
            return _query

        _query = {
            'filtered': {
                'query': _query,
                'filter': {
                    "terms": {
                        "taxid": self.species
                    }
                }
            }
        }
        return _query

    # keepit (?)
    def get_query_filters(self):
        '''filters added here will be applied in a filtered query,
           thus will affect the facet counts.
        '''
        filters = []
        #species filter
        if self.species and self.species != 'all':
            if len(self.species) == 1:
                filters.append({
                    "term": {"taxid": self.species[0]}
                })
            else:
                filters.append({
                    "terms": {"taxid": self.species}
                })
        if self.entrezonly:
            filters.append({
                "exists": {"field": "entrezgene"}
            })
        if self.ensemblonly:
            filters.append({
                "exists": {"field": "ensemblgene"}
            })

        if self.userfilter:
            _uf = UserFilters()
            for _fname in self.userfilter:
                _filter = _uf.get(_fname)
                if _filter:
                    filters.append(_filter['filter'])

        if self.existsfilter:
            for _filter in self.existsfilter:
                filters.append({
                    "exists": {"field": _filter}
                })
        if self.missingfilter:
            for _filter in self.missingfilter:
                filters.append({
                    "missing": {"field": _filter}
                })

        if filters:
            if len(filters) == 1:
                filters = filters[0]
            else:
                #concatenate multiple filters with "and" filter
                filters = {"and": filters}

        return filters

    # keepit (?)
    def add_query_filters(self, _query):
        '''filters added here will be applied in a filtered query,
           thus will affect the facet counts.
        '''
        filters = self.get_query_filters()
        if not filters:
            return _query

        #add filters as filtered query
        #this will apply to facet counts
        _query = {
            'filtered': {
                'query': _query,
                'filter': filters
            }
        }

        return _query

    # keepit
    def add_facet_filters(self, _query):
        """To add filters (e.g. taxid) to restrict returned hits,
            but does not change the scope for facet counts.
        """
        filters = []
        #species_facet_filter
        if self.species_facet_filter:
            if len(self.species) == 1:
                filters.append({
                    "term": {"taxid": self.species_facet_filter[0]}
                })
            else:
                filters.append({
                    "terms": {"taxid": self.species_facet_filter}
                })
        if filters:
            if len(filters) == 1:
                filters = filters[0]
            else:
                #concatenate multiple filters with "and" filter
                filters = {"and": filters}

            #this will not change facet counts
            _query["filter"] = filters

        return _query

    # keepit
    def add_species_custom_filters_score(self, _query):
        _query = {
            "function_score": {
                "query": _query,
                "functions": [
                    #downgrade "pseudogene" matches
                    {
                        "filter": {"term": {"name": "pseudogene"}},
                        "boost_factor": "0.5"
                    },
                    {
                        "filter": {"term": {"taxid": 9606}},
                        "boost_factor": "1.55"
                    },
                    {
                        "filter": {"term": {"taxid": 10090}},
                        "boost_factor": "1.3"
                    },
                    {
                        "filter": {"term": {"taxid": 10116}},
                        "boost_factor": "1.1"
                    },
                ],
                "score_mode": "first"
            }
        }
        return _query

    # keepit (?)
    def build(self, q, mode=1):
        '''mode:
                1    match query
                2    wildcard query
                3    raw_string query

               else  string_query (for test)
        '''
        if q == '__all__':
            _query = {"match_all": {}}
        else:
            if mode == 1:
                _query = self.dis_max_query(q)
            elif mode == 2:
                _query = self.wildcard_query(q)
            elif mode == 3:
                _query = self.raw_string_query(q)
            else:
                _query = self.string_query(q)

        _query = self.add_query_filters(_query)
        _query = self.add_species_custom_filters_score(_query)
        _q = {'query': _query}
        _q = self.add_facet_filters(_q)
        if self.options:
            _q.update(self.options)
        return _q

    # keepit (but similar)
    def build_id_query(self, id, scopes=None):
        id_is_int = is_int(id)
        if scopes is None:
            #by default search three fields ['entrezgene', 'ensemblgene', 'retired']
            if id_is_int:
                _query = {
                    "multi_match": {
                        "query": id,
                        "fields": ['entrezgene', 'retired']
                    }
                }
            else:
                _query = {
                    "match": {
                        "ensemblgene": {
                            "query": u"{}".format(id),
                            "operator": "and"
                        }
                    }
                }
        else:
            if is_str(scopes):
                _field = scopes
                if _field in ['entrezgene', 'retired']:
                    if id_is_int:
                        _query = {
                            "match": {
                                _field: id
                            }
                        }
                    else:
                        #raise ValueError('fields "%s" requires an integer id to query' % _field)
                        #using a fake query here to make sure return empty hits
                        _query = self._nohits_query
                else:
                    _query = {
                        "match": {
                            _field: {
                                "query": u"{}".format(id),
                                "operator": "and"
                            }
                        }
                    }
            elif is_seq(scopes):
                int_fields = []
                str_fields = copy.copy(scopes)
                if 'entrezgene' in str_fields:
                    int_fields.append('entrezgene')
                    str_fields.remove('entrezgene')
                if 'retired' in str_fields:
                    int_fields.append('retired')
                    str_fields.remove('retired')

                if id_is_int:
                    if len(int_fields) == 1:
                        _query = {
                            "match": {
                                int_fields[0]: id
                            }
                        }
                    elif len(int_fields) == 2:
                        _query = {
                            "multi_match": {
                                "query": id,
                                "fields": int_fields
                            }
                        }
                    else:
                        _query = self._nohits_query
                elif str_fields:
                    _query = {
                        "multi_match": {
                            "query": u"{}".format(id),
                            "fields": str_fields,
                            "operator": "and"
                        }
                    }
                else:
                    _query = self._nohits_query

            else:
                raise ValueError('"scopes" cannot be "%s" type' % type(scopes))

        #_query = self.add_species_filter(_query)
        _query = self.add_query_filters(_query)
        _query = self.add_species_custom_filters_score(_query)
        _q = {"query": _query}
        if self.options:
            _q.update(self.options)

        # if 'fields' in _q and _q['fields'] is not None:
        #     _q['_source'] = _q['fields']
        #     del _q['fields']
        return _q

    def build_multiple_id_query(self, id_list, scopes=None):
        """make a query body for msearch query."""
        _q = []
        for id in id_list:
            _q.extend(['{}', json.dumps(self.build_id_query(id, scopes))])
        _q.append('')
        return '\n'.join(_q)

    # TODO: used ?
    def build_multiple_id_query2(self, id_list, scopes=None):
        _query = {
            "terms": {
                ("%s" % scopes): id_list,
            }
        }
        #_query = self.add_species_filter(_query)
        _query = self.add_query_filters(_query)
        _query = self.add_species_custom_filters_score(_query)
        _q = {"query": _query}
        if self.options:
            _q.update(self.options)
        return _q

    # keepit
    def build_genomic_pos_query(self, chr, gstart, gend, assembly=None):
        '''By default if assembly is None, the lastest assembly is used.
           for some species (e.g. human) we support multiple assemblies,
           exact assembly is passed as well.
        '''
        gstart = safe_genome_pos(gstart)
        gend = safe_genome_pos(gend)
        if chr.lower().startswith('chr'):
            chr = chr[3:]

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
                            {
                                "term": {genomic_pos_field + ".chr": chr.lower()}
                            },
                            {
                                "range": {genomic_pos_field + ".start": {"lte": gend}}
                            },
                            {
                                "range": {genomic_pos_field + ".end": {"gte": gstart}}
                            }
                        ]
                    }
                }
            }
        }
        # _query = {
        #     'filtered': {
        #         'query': _query,
        #         'filter' : {
        #             "term" : {"taxid" : taxid}
        #         }
        #     }
        # }
        _query = self.add_query_filters(_query)
        _q = {'query': _query}
        if self.options:
            _q.update(self.options)
        return _q

    # same exist in biothings.ESQuery ?
    def _parse_sort_option(self, options):
        sort = options.get('sort', None)
        if sort:
            _sort_array = []
            for field in sort.split(','):
                field = field.strip()
                if field == 'name' or field[1:] == 'name':
                    # sorting on "name" field is ignored, as it is a multi-text field.
                    continue
                if field.startswith('-'):
                    _f = {"%s" % field[1:]: "desc"}
                else:
                    _f = {"%s" % field: "asc"}
                _sort_array.append(_f)
            options["sort"] = _sort_array
        return options

    # same exist in biothings.ESQuery ?
    def _parse_facets_option(self, options):
        facets = options.get('facets', None)
        if facets:
            _facets = {}
            for field in facets.split(','):
                _facets[field] = {"terms": {"field": field}}
            options["facets"] = _facets
        return options


from biothings.settings import BiothingSettings
from biothings.utils.es import get_es
biothing_settings = BiothingSettings()
class UserFilters(object):
    def __init__(self):
        self.conn = get_es(biothing_settings.es_host) 
        self.ES_INDEX_NAME = 'userfilters'
        self.ES_DOC_TYPE = 'filter'
        self._MAPPING = {
            "dynamic": False,
            "properties": {}
        }   # this mapping disables indexing completely since we don't need it.

    def create(self):
        print("Creating index...",)
        print(self.conn.create_index(self.ES_INDEX_NAME))
        print("Updating mapping...",)
        print(self.conn.put_mapping(self.ES_DOC_TYPE,
                                    self._MAPPING,
                                    [self.ES_INDEX_NAME]))

    def add(self, name, id_list=[], id_field="entrezgene", raw_filter=None):
        '''add a named filter.'''
        _filter = None
        if raw_filter:
            _filter = raw_filter
        elif id_list and id_field:
            _filter = {
                "terms": {id_field: id_list}
            }
        if _filter:
            print('Adding filter "{}"...'.format(name),)
            _doc = {'_id': name,
                    'filter': _filter}
            print(self.conn.index(_doc, self.ES_INDEX_NAME,
                                  self.ES_DOC_TYPE,
                                  id=_doc['_id']))
        else:
            print("No filter to add.")

    def get(self, name):
        '''get a named filter.'''
        try:
            return self.conn.get(self.ES_INDEX_NAME, name, self.ES_DOC_TYPE)['_source']
        except NotFoundError:
            return None

    def count(self):
        n = self.conn.count(None, self.ES_INDEX_NAME, self.ES_DOC_TYPE)['count']
        return n

    def get_all(self, skip=0, size=1000):
        '''get all named filter.'''
        print('\ttotal filters: {}'.format(self.count()))
        q = {"query": {"match_all": {}}}
        res = self.conn.search_raw(q, indices=self.ES_INDEX_NAME, doc_types=self.ES_DOC_TYPE,
                                   **{"from": str(skip), "size": str(1000)})
        return [hit['_source'] for hit in res.hits.hits]

    def delete(self, name, noconfirm=False):
        '''delete a named filter.'''
        _filter = self.get(name)
        if _filter:
            msg = 'Found filter "{}". Continue to delete it?'.format(name)
            if noconfirm or ask(msg) == 'Y':
                print('Deleting filter "{}"...'.format(name),)
                print(self.conn.delete(self.ES_INDEX_NAME, self.ES_DOC_TYPE, name))
        else:
            print('Filter "{}" does not exist. Abort now.'.format(name))

    def rename(self, name, newname):
        '''"rename" a named filter.
           Basically, this needs to create a new doc and delete the old one.
        '''
        _filter = self.get(name)
        if _filter:
            msg = 'Found filter "{}". Rename it to "{}"?'.format(name, newname)
            if ask(msg) == 'Y':
                self.add(newname, raw_filter=_filter['filter'])
                self.delete(name, noconfirm=True)
        else:
            print('Filter "{}" does not exist. Abort now.'.format(name))


def make_test_index():

    def get_sample_gene(gene):
        qbdr = ESQueryBuilder(fields=['_source'], size=1000)
        _query = qbdr.dis_max_query(gene)
        _query = qbdr.add_species_custom_filters_score(_query)
        _q = {'query': _query}
        if qbdr.options:
            _q.update(qbdr.options)

        esq = ESQuery()
        res = esq._search(_q)
        return [h['_source'] for h in res['hits']['hits']]

    gli = get_sample_gene('CDK2') + \
        get_sample_gene('BTK') + \
        get_sample_gene('insulin')

    from utils.es import ESIndexer
    index_name = 'genedoc_2'
    index_type = 'gene_sample'
    esidxer = ESIndexer(None, None)
    conn = esidxer.conn
    try:
        esidxer.delete_index_type(index_type)
    except:
        pass
    mapping = dict(conn.get_mapping('gene', index_name)['gene'])
    print(conn.put_mapping(index_type, mapping, [index_name]))

    print("Building index...")
    cnt = 0
    for doc in gli:
        conn.index(doc, index_name, index_type, doc['_id'])
        cnt += 1
        print(cnt, ':', doc['_id'])
    print(conn.flush())
    print(conn.refresh())
    print('Done! - {} docs indexed.'.format(cnt))
