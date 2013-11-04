"""Module to query ES indexes"""

#http://www.elasticsearch.org/guide/reference/query-dsl/custom-filters-score-query.html
#http://www.elasticsearch.org/guide/reference/query-dsl/custom-score-query.html
#http://www.elasticsearch.org/guide/reference/query-dsl/custom-boost-factor-query.html
#http://www.elasticsearch.org/guide/reference/query-dsl/boosting-query.html

import types
import json
import re
import time
import copy

from pyes import ES
from pyes.exceptions import NotFoundException, ElasticSearchException
from pyes.utils import make_path
from pyes.query import MatchAllQuery, StringQuery

from config import ES_HOST, ES_INDEX_NAME_TIER1, ES_INDEX_NAME_ALL, ES_INDEX_TYPE
from utils.common import ask, is_int, timesofar, safe_genome_pos, dotdict, taxid_d
from utils.dotfield import parse_dot_fields


def get_es():
    conn = ES(ES_HOST, default_indices=[ES_INDEX_NAME_ALL],
              timeout=120.0, max_retries=10)
    return conn


es = get_es()


dummy_model = lambda es, res: res

class MGQueryError(Exception):
    pass

class ESQuery:
    def __init__(self):
        #self.conn0 = es0
        self.conn = es
        self.conn.model = dummy_model
        # self._index = 'genedoc_mygene'
        # self._index = 'genedoc_mygene_allspecies'
        # self._doc_type = 'gene'
        self._index = ES_INDEX_NAME_ALL
        self._doc_type = ES_INDEX_TYPE

        #self._doc_type = 'gene_sample'
        self._default_fields = ['name', 'symbol', 'taxid', 'entrezgene', 'ensemblgene']
        #self._default_species = [9606, 10090, 10116, 7227, 6239]  #human, mouse, rat, fruitfly, celegan
        self._default_species = [9606, 10090, 10116]              #human, mouse, rat
        self._tier_1_species = set(taxid_d.values())

    def _search(self, q, species='all'):
        self._set_index(species)
        res = self.conn.search_raw(q, indices=self._index, doc_types=self._doc_type)
        self._index = ES_INDEX_NAME_ALL     #reset self._index
        return res

    def _msearch(self, q, species='all'):
        self._set_index(species)
        path = make_path((self._index, self._doc_type, '_msearch'))
        res = self.conn._send_request('GET', path, body=q)
        self._index = ES_INDEX_NAME_ALL     #reset self._index
        return res

    def _set_index(self, species):
        '''set proper index for given species parameter.'''
        if species == 'all' or len(set(species)-self._tier_1_species) > 0:
            self._index = ES_INDEX_NAME_ALL
        else:
            self._index = ES_INDEX_NAME_TIER1

    def _get_genedoc(self, hit, dotfield=True):
        doc = hit.get('_source', hit.get('fields', {}))
        doc.setdefault('_id', hit['_id'])
        if '_version' in hit:
            doc.setdefault('_version', hit['_version'])
        if not dotfield:
            doc = parse_dot_fields(doc)
        return doc

    def _cleaned_res(self, res, empty=[], error={'error': True}, single_hit=False, dotfield=True):
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

    def _cleaned_fields(self, fields):
        '''return a cleaned fields parameter.
            should be either None (return all fields) or a list fields.
        '''
        if fields:
            if type(fields) in types.StringTypes:
                if fields.lower() == 'all':
                    fields = None     # all fields will be returned.
                else:
                    fields = [x.strip() for x in fields.split(',')]
        else:
            fields = self._default_fields
        return fields

    def _cleaned_species(self, species, default_to_none=False):
        '''return a cleaned species parameter.
           should be either "all" or a list of taxids/species_names, or a single taxid/species_name.
           returned species is always a list of taxids (even when only one species)
        '''
        if species is None:
            #set to default_species
            return None if default_to_none else self._default_species
        if type(species) is types.IntType:
            return [species]

        if type(species) in types.StringTypes:
            if species.lower() == 'all':
                #if self.species == 'all': do not apply species filter, all species is included.
                return species.lower()
            else:
                species = [s.strip().lower() for s in species.split(',')]

        if type(species) not in [types.ListType, types.TupleType]:
            raise ValueError('"species" parameter must be a string, integer or a list/tuple, not "{}".'.format(type(species)))

        _species = []
        for s in species:
            if is_int(s):
                _species.append(int(s))
            elif s in taxid_d:
                _species.append(taxid_d[s])
        return _species

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
                return mat.groupdict()

    def _is_wildcard_query(self, query):
        '''Return True if input query is a wildcard query.'''
        return query.find('*') != -1 or query.find('?') != -1

    def _is_raw_string_query(self, query):
        '''Return True if input query is a wildchar/fielded/boolean query.'''
        for v in [':','~', ' AND ', ' OR ', 'NOT ']:
            if query.find(v) != -1:
                return True
        if query.startswith('"') and query.endswith('"'):
            return True
        return False

    def _get_cleaned_query_options(self, fields, kwargs):
        """common helper for processing fields, kwargs and other options passed to ESQueryBuilder."""
        options = dotdict()
        options.raw = kwargs.pop('raw', False)
        options.rawquery = kwargs.pop('rawquery', False)
        #if dofield is false, returned fields contains dot notation will be restored as an object.
        options.dotfield = kwargs.pop('dotfield', True) not in [False, 'false']
        scopes = kwargs.pop('scopes', None)
        if scopes:
            options.scopes = self._cleaned_fields(scopes)
        kwargs["fields"] = self._cleaned_fields(fields)
        #if no dotfield in "fields", set dotfield always be True, i.e., no need to parse dotfield
        if not options.dotfield:
            _found_dotfield = False
            if kwargs['fields']:
                for _f in kwargs['fields']:
                    if _f.find('.') != -1:
                        _found_dotfield = True
                        break
            if not _found_dotfield:
                options.dotfield = True

        #this species parameter is added to the query, thus will change facet counts.
        kwargs['species'] = self._cleaned_species(kwargs.get('species', None))

        #this parameter is to add species filter without changing facet counts.
        kwargs['species_facet_filter'] = self._cleaned_species(kwargs.get('species_facet_filter', None),
                                                               default_to_none=True)

        options.kwargs = kwargs
        return options

    def get_gene(self, geneid, fields='all', **kwargs):
        kwargs['fields'] = self._cleaned_fields(fields)
        raw = kwargs.pop('raw', False)
        #res = self.conn0.get(self._index, self._doc_type, geneid, **kwargs)
        try:
            res = self.conn.get(self._index, self._doc_type, geneid, **kwargs)
        except NotFoundException:
            return None
        return res if raw else self._get_genedoc(res)

    def mget_gene(self, geneid_list, fields=None, **kwargs):
        kwargs['fields'] = self._cleaned_fields(fields)
        raw = kwargs.pop('raw', False)
        res = self.conn.mget(geneid_list, self._index, self._doc_type, **kwargs)
        return res if raw else [self._get_genedoc(doc) for doc in res]

    def get_gene2(self, geneid, fields='all', **kwargs):
        '''for /gene/<geneid>'''
        options = self._get_cleaned_query_options(fields, kwargs)
        qbdr = ESQueryBuilder(**options.kwargs)
        _q = qbdr.build_id_query(geneid, options.scopes)
        if options.rawquery:
            return _q
        res =  self._search(_q, species=options.kwargs['species'])
        if not options.raw:
            res = self._cleaned_res(res, empty=None, single_hit=True, dotfield=options.dotfield)
        return res

    def mget_gene2(self, geneid_list, fields=None, **kwargs):
        '''for /query post request'''
        options = self._get_cleaned_query_options(fields, kwargs)
        qbdr = ESQueryBuilder(**options.kwargs)
        try:
            _q = qbdr.build_multiple_id_query(geneid_list, options.scopes)
        except MGQueryError as err:
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
            hits = self._cleaned_res(hits, empty=[], single_hit=False, dotfield=options.dotfield)
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
        options = self._get_cleaned_query_options(fields, kwargs)
        qbdr = ESQueryBuilder(**options.kwargs)
        q = q.strip()
        q = re.sub(u'[\t\n\x0b\x0c\r]+', ' ', q)
        _q = None
        # Check if special interval query pattern exists
        interval_query = self._parse_interval_query(q)
        try:
            if interval_query:
                #should also passing a "taxid" along with interval.
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
                _q = qbdr.build(q, mode=3)   #raw string query
            elif self._is_wildcard_query(q):
                _q = qbdr.build(q, mode=2)   #wildcard query
            else:
            # normal text query
                _q = qbdr.build(q, mode=1)
        except MGQueryError as err:
            return {'success': False,
                    'error': err.message}

        if _q:
            if options.rawquery:
                return _q

            try:
                res = self._search(_q, species=kwargs['species'])
            except ElasticSearchException as err:
                err_msg = err.message if options.raw else "invalid query term."
                return {'success': False,
                        'error': err_msg}

            if not options.raw:
                _res = res['hits']
                _res['took'] = res['took']
                if "facets" in res:
                    _res['facets'] = res['facets']
                for v in _res['hits']:
                    del v['_type']
                    del v['_index']
                    for attr in ['fields', '_source']:
                        if attr in v:
                            v.update(v[attr])
                            del v[attr]
                            break
                    if not options.dotfield:
                        parse_dot_fields(v)
                res = _res
        else:
            res = {'success': False, 'error': "Invalid query. Please check parameters."}

        return res

    def query_interval(self, taxid, chr,  gstart, gend, **kwargs):
        '''deprecated! Use query method with interval query string.'''
        kwargs.setdefault('fields', ['symbol','name','taxid'])
        rawquery = kwargs.pop('rawquery', None)
        qbdr = ESQueryBuilder(**kwargs)
        _q = qbdr.build_genomic_pos_query(taxid, chr,  gstart, gend)
        if rawquery:
            return _q
        return self._search(_q)

    def doc_feeder(self, step=1000, s=None, e=None, inbatch=False, query=None, **kwargs):
        '''A iterator for returning docs in a ES index with batch query.
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
                raw_res = self.conn.search_raw(q, self._index, self._doc_type,
                      start=s, size=step, scan=True, scroll='5m', **kwargs)
                n = raw_res['hits']['total']
                print 'Retrieving %d documents from index "%s/%s".' % (n, self._index, self._doc_type)
            else:
                raw_res = self.conn.search_scroll(raw_res._scroll_id, scroll='5m')
            hits_cnt = len(raw_res['hits']['hits'])
            if hits_cnt == 0:
                break
            else:

                print "Processing %d-%d documents..." % (cnt+1, cnt+hits_cnt) ,
                res = self._cleaned_res(raw_res)
                if inbatch:
                    yield res
                else:
                    for hit in res:
                        yield hit
                cnt += hits_cnt
                print 'Done.[%.1f%%,%s]' % (cnt*100./n, timesofar(t1))
                if e and cnt > e:
                    break

        print "="*20
        print 'Finished.[total docs: %s, total time: %s]' % (cnt, timesofar(t0))


    def metadata(self, raw=False):
        '''return metadata about the index.'''
        mapping = self.conn.indices.get_mapping(self._doc_type, self._index)
        if raw:
            return mapping

        def get_fields(properties):
            for k, v in properties.items():
                if 'properties' in v:
                    for f in get_fields(v['properties']):
                        yield f
                else:
                    if v.get('index', None) == 'no':
                        continue
                    f = v.get('index_name', k)
                    yield f

        field_set = set(get_fields(mapping[self._doc_type]['properties']))
        metadata = {
            'available_fields': sorted(field_set)
        }
        if '_meta' in mapping[self._doc_type]:
            metadata.update(mapping[self._doc_type]['_meta'])
        return metadata


class ESQueryBuilder():
    def __init__(self, **query_options):
        """You can pass these options:
            fields     default ['name', 'symbol', 'taxid', 'entrezgene', 'ensemblgene']
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

        """
        self.options = query_options
        self.species = self.options.pop('species', 'all')   #species should be either 'all' or a list of taxids.
        self.species_facet_filter = self.options.pop('species_facet_filter', None)
        self.entrezonly = self.options.pop('entrezonly', False)
        self.ensemblonly = self.options.pop('ensemblonly', False)
        userfilter = self.options.pop('userfilter', None)
        self.userfilter = userfilter.split(',') if userfilter else None
        self._parse_sort_option(self.options)
        self._parse_facets_option(self.options)
        self._allowed_options = ['fields', 'start', 'from', 'size',
                                 'sort', 'explain', 'version', 'facets']
        for key in set(self.options) - set(self._allowed_options):
                del self.options[key]

        #this is a fake query to make sure to return empty hits
        self._nohits_query = {
                            "match": {
                                'non_exist_field': ''
                            }
                        }

    def _parse_sort_option(self, options):
        sort = options.get('sort', None)
        if sort:
            _sort_array = []
            for field in sort.split(','):
                field = field.strip()
                if field == 'name' or field[1:]=='name':
                    #sorting on "name" field is ignored, as it is a multi-text field.
                    continue
                if field.startswith('-'):
                    _f = {"%s" % field[1:]: "desc"}
                else:
                    _f = {"%s" % field: "asc"}
                _sort_array.append(_f)
            options["sort"] = _sort_array
        return options

    def _parse_facets_option(self, options):
        facets = options.get('facets', None)
        if facets:
            _facets = {}
            for field in facets.split(','):
                _facets[field]= {"terms": {"field": field}}
            options["facets"] = _facets
        return options

    def dis_max_query(self, q):
        #remove '"' and '\' from q, they will break json decoder.
        q = q.replace('"','').replace('\\', '')
        _query = {
            "dis_max" : {
                "tie_breaker" : 0,
                "boost" : 1,
                "queries" : [
                    {
                    "custom_boost_factor": {
                        "query" : {
                            "match" : { "symbol" : {
                                            "query": "%(q)s",
                                            "analyzer": "whitespace_lowercase"
                                            }
                                      },
                        },
                        "boost_factor": 5
                    }
                    },
                    {
                    "custom_boost_factor": {
                        "query" : {
                            #This makes phrase match of "cyclin-dependent kinase 2" appears first
                            "match_phrase" : { "name" : "%(q)s"},
                        },
                        "boost_factor": 4
                    }
                    },
                    {
                    "custom_boost_factor": {
                        "query" : {
                            "match" : { "name" : {
                                            "query": "%(q)s",
                                            "analyzer": "whitespace_lowercase"
                                            }
                                      },
                        },
                        "boost_factor" : 3
                    }
                    },
                    {
                    "custom_boost_factor": {
                        "query" : {
                            "match" : { "unigene" : {
                                                    "query": "%(q)s" ,
                                                    "analyzer": "string_lowercase"
                                                 }
                                             }
                        },
                        "boost_factor": 1.1
                    }
                    },
                    {
                    "custom_boost_factor": {
                        "query" : {
                            "match" : { "go" : {
                                                    "query": "%(q)s" ,
                                                    "analyzer": "string_lowercase"
                                                 }
                                             }
                        },
                        "boost_factor": 1.1
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
                    "custom_boost_factor": {
                        "query" : {
                            "query_string" : {
                                            "query": "%(q)s",
                                            "default_operator": "AND",
                                            "auto_generate_phrase_queries": True
                            },
                        },
                        "boost_factor": 1
                    }
                    },

                ]
            }
            }
        _query = json.dumps(_query)
        _query = json.loads(_query % {'q': q})

        if is_int(q):
            _query['dis_max']['queries'] = []
            _query['dis_max']['queries'].insert(0,
                    {
                    "custom_boost_factor": {
                        "query" : {
                            "term" : { "entrezgene" : int(q)},
                        },
                        "boost_factor": 8
                    }
                    }
                    )


        return _query

    def wildcard_query(self, q):
        '''q should contains either * or ?, but not the first character.'''
        _query = {
            "dis_max" : {
                "tie_breaker" : 0,
                "boost" : 1,
                "queries" : [
                    {
                    "custom_boost_factor": {
                        "query" : {
                            "wildcard" : { "symbol" : {
                                            "value": "%(q)s",
                                            "boost": 5.0,
                                            }
                            },
                        },
                    }
                    },
                    {
                    "custom_boost_factor": {
                        "query" : {
                            "wildcard" : { "name" : {
                                           "value": "%(q)s",
                                           "boost": 1.1,
                                            }
                            },
                        }
                    }
                    },
                    {
                    "custom_boost_factor": {
                        "query" : {
                            "wildcard" : { "summary" : {
                                           "value": "%(q)s",
                                           "boost": 0.5,
                                            }
                            },
                        }
                    }
                    },

                ]
            }
            }
        _query = json.dumps(_query)
        _query = json.loads(_query % {'q': q.lower()})

        return _query

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

    def raw_string_query(self, q):
        _query = {
            "query_string": {
                "query": "%(q)s",
#                "analyzer": "string_lowercase",
                "default_operator": "AND",
                "auto_generate_phrase_queries": True
            }
        }
        _query = json.dumps(_query)
        try:
            _query = json.loads(_query % {'q': q.replace('"', '\\"')})
        except ValueError:
            raise MGQueryError("invalid query term.")
        return _query

    def add_species_filter(self, _query):
        """deprecated! replaced by  """
        if self.species == 'all':
            #do not apply species filter
            return _query

        _query = {
            'filtered': {
                'query': _query,
                'filter' : {
                    "terms" : {
                        "taxid" : self.species
                    }
                }
            }
        }
        return _query

    def get_query_filters(self):
        '''filters added here will be applied in a filtered query,
           thus will affect the facet counts.
        '''
        filters = []
        #species filter
        if self.species and self.species != 'all':
            if len(self.species) == 1:
                filters.append({
                     "term" : {"taxid" : self.species[0] }
                    })
            else:
                filters.append({
                     "terms" : {"taxid" : self.species }
                    })
        if self.entrezonly:
            filters.append({
                 "exists" : { "field" : "entrezgene" }
                })
        if self.ensemblonly:
            filters.append({
                 "exists" : { "field" : "ensemblgene" }
                })

        if self.userfilter:
            _uf = UserFilters()
            for _fname in self.userfilter:
                _filter = _uf.get(_fname)
                if _filter:
                    filters.append(_filter['filter'])

        if filters:
            if len(filters) == 1:
                filters = filters[0]
            else:
                #concatenate multiple filters with "and" filter
                filters = {"and": filters}

        return filters

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
                'filter' : filters
            }
        }

        return _query

    def add_facet_filters(self, _query):
        """To add filters (e.g. taxid) to restrict returned hits,
            but does not change the scope for facet counts.
        """
        filters = []
        #species_facet_filter
        if self.species_facet_filter:
            if len(self.species) == 1:
                filters.append({
                     "term" : {"taxid" : self.species_facet_filter[0] }
                    })
            else:
                filters.append({
                     "terms" : {"taxid" : self.species_facet_filter }
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


    def add_species_custom_filters_score(self, _query):
        _query = {
            "custom_filters_score": {
            "query": _query,
            "filters" : [
                #downgrade "pseudogene" matches
                {
                    "filter" : { "term" : { "name" : "pseudogene" } },
                    "boost" : "0.5"
                },

                {
                    "filter" : { "term" : { "taxid" : 9606 } },
                    "boost" : "1.55"
                },
                {
                    "filter" : { "term" : { "taxid" : 10090 } },
                    "boost" : "1.3"
                },
                {
                    "filter" : { "term" : { "taxid" : 10116 } },
                    "boost" : "1.1"
                },
            ],
            "score_mode" : "first"
            }
        }
        return _query

    def build(self, q, mode=1):
        '''mode:
                1    match query
                2    wildcard query
                3    raw_string query

               else  string_query (for test)
        '''
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
                        "ensemblgene": "%s" % id
                    }
                }
                # _query = {
                #     "query_string": {
                #         "query": "%s" % id,
                #     }
                # }

        else:
            if type(scopes) in types.StringTypes:
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
                            _field: "%s" % id
                        }
                    }
            elif type(scopes) in (types.ListType, types.TupleType):
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
                            "query": "%s" % id,
                            "fields": str_fields
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
        return _q

    def build_multiple_id_query(self, id_list, scopes=None):
        """make a query body for msearch query."""
        _q = []
        for id in id_list:
            _q.extend(['{}', json.dumps(self.build_id_query(id, scopes))])
        _q.append('')
        return '\n'.join(_q)

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

    def build_genomic_pos_query(self, chr, gstart, gend):
        gstart = safe_genome_pos(gstart)
        gend = safe_genome_pos(gend)
        if chr.lower().startswith('chr'):
            chr = chr[3:]
        _query = {
                   "nested" : {
                       "path" : "genomic_pos",
                       "query" : {
                            "bool" : {
                                "must" : [
                                    {
                                        "term" : {"genomic_pos.chr" : chr.lower()}
                                    },
                                    {
                                        "range" : {"genomic_pos.start" : {"lte" : gend}}
                                    },
                                    {
                                        "range" : {"genomic_pos.end" : {"gte" : gstart}}
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

class UserFilters:
    def __init__(self):
        self.conn = es
        self.ES_INDEX_NAME = 'userfilters'
        self.ES_INDEX_TYPE = 'filter'
        self._MAPPING = {
           "dynamic": False,
           "properties": {}
        }   #this mapping disables indexing completely since we don't need it.

    def create(self):
        print "Creating index...",
        print self.conn.create_index(self.ES_INDEX_NAME)
        print "Updating mapping...",
        print self.conn.put_mapping(self.ES_INDEX_TYPE ,
                                    self._MAPPING,
                                    [self.ES_INDEX_NAME])

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
            print 'Adding filter "{}"...'.format(name),
            _doc = {'_id': name,
                    'filter': _filter}
            print self.conn.index(_doc, self.ES_INDEX_NAME,
                                  self.ES_INDEX_TYPE,
                                  id=_doc['_id'])
        else:
            print "No filter to add."

    def get(self, name):
        '''get a named filter.'''
        try:
            return self.conn.get(self.ES_INDEX_NAME, self.ES_INDEX_TYPE, name)['_source']
        except NotFoundException:
            return None

    def count(self):
        n = self.conn.count(None, self.ES_INDEX_NAME, self.ES_INDEX_TYPE)['count']
        return n

    def get_all(self, skip=0, size=1000):
        '''get all named filter.'''
        print '\ttotal filters: {}'.format(self.count())
        q = {"query": {"match_all": {}}}
        res = self.conn.search_raw(q, indices=self.ES_INDEX_NAME, doc_types=self.ES_INDEX_TYPE,
                              **{"from": str(skip), "size": str(1000)})
        return [hit['_source'] for hit in res.hits.hits]

    def delete(self, name, noconfirm=False):
        '''delete a named filter.'''
        _filter = self.get(name)
        if _filter:
            msg = 'Found filter "{}". Continue to delete it?'.format(name)
            if noconfirm or ask(msg) == 'Y':
                print 'Deleting filter "{}"...'.format(name),
                print self.conn.delete(self.ES_INDEX_NAME, self.ES_INDEX_TYPE, name)
        else:
            print 'Filter "{}" does not exist. Abort now.'.format(name)

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
            print 'Filter "{}" does not exist. Abort now.'.format(name)


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
          get_sample_gene('BTK')  + \
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
    print conn.put_mapping(index_type, mapping, [index_name])

    print "Building index..."
    cnt = 0
    for doc in gli:
        conn.index(doc, index_name, index_type, doc['_id'])
        cnt += 1
        print cnt, ':', doc['_id']
    print conn.flush()
    print conn.refresh()
    print 'Done! - {} docs indexed.'.format(cnt)
