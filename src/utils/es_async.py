import re
import json

import tornado.web
import tornado.httpclient
tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
import tornadoes

from utils.es import (ESQuery, ESQueryBuilder,
                      MGQueryError, ElasticSearchException,
                      ES_INDEX_NAME_ALL)
from utils.dotfield import parse_dot_fields
from config import ES_HOST


class ESQueryAsync(ESQuery):
    es_connection = tornadoes.ESConnection(ES_HOST.split(':')[0])
    es_connection.httprequest_kwargs = {'request_timeout': 120.}  # increase default timeout from 20 to 120s

    def _search_async(self, q, species='all', callback=None):
        self._set_index(species)
        self.es_connection.search(callback=callback,
                                  index=self._index,
                                  type=self._doc_type,
                                  source=q)

    def _msearch_async(self, q, species='all', callback=None):
        self._set_index(species)
        path = '/'.join((self.es_connection.url, self._index, self._doc_type, '_msearch'))
        request_http = tornadoes.HTTPRequest(path, method="POST", body=q,
                                             **self.es_connection.httprequest_kwargs)
        self.es_connection.client.fetch(request=request_http, callback=callback)
        self._index = ES_INDEX_NAME_ALL     # reset self._index

    def get_gene2(self, geneid, fields='all', **kwargs):
        '''for /gene/<geneid>'''
        callback = kwargs.pop('callback', None)
        is_async = callback is not None

        options = self._get_cleaned_query_options(fields, kwargs)
        qbdr = ESQueryBuilder(**options.kwargs)
        _q = qbdr.build_id_query(geneid, options.scopes)
        if options.rawquery:
            if is_async:
                callback(_q)
                return
            else:
                return _q
        if is_async:
            def inner_callback(response):
                res = json.loads(response.body)
                if not options.raw:
                    res = self._cleaned_res(res, empty=None, single_hit=True, dotfield=options.dotfield)
                callback(res)
            self._search_async(_q, species=options.kwargs['species'], callback=inner_callback)
            return
        else:
            res = self._search(_q)
            if not options.raw:
                res = self._cleaned_res(res, empty=None, single_hit=True, dotfield=options.dotfield)
            return res

    def _normalize_msearch_res(self, res, geneid_list, options):
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

    def mget_gene2(self, geneid_list, fields=None, **kwargs):
        '''for /query post request'''
        callback = kwargs.pop('callback', None)
        is_async = callback is not None

        options = self._get_cleaned_query_options(fields, kwargs)
        qbdr = ESQueryBuilder(**options.kwargs)
        try:
            _q = qbdr.build_multiple_id_query(geneid_list, options.scopes)
        except MGQueryError as err:
            res = {'success': False,
                   'error': err.message}
            if is_async:
                callback(res)
                return
            else:
                return res
        if options.rawquery:
            if is_async:
                callback(_q)
                return
            else:
                return _q
        if is_async:
            def inner_callback(response):
                if response.code == 599 and response.body is None:
                    res = {'success': False,
                           'error': 'timeout'}
                else:
                    res = json.loads(response.body)['responses']
                    if not options.raw:
                        res = self._normalize_msearch_res(res, geneid_list, options)
                callback(res)
            self._msearch_async(_q, species=kwargs['species'], callback=inner_callback)
            return
        else:
            res = self._msearch(_q, kwargs['species'])['responses']
            return res if options.raw else self._normalize_msearch_res(res, geneid_list, options)

    @staticmethod
    def _normalize_query_res(res, options):
        if "error" in res:
            return {'success': False,
                    'error': "invalid query term."}

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
        return res

    def query(self, q, fields=None, **kwargs):
        '''for /query?q=<query>'''
        callback = kwargs.pop('callback', None)
        is_async = callback is not None

        options = self._get_cleaned_query_options(fields, kwargs)
        qbdr = ESQueryBuilder(**options.kwargs)
        q = re.sub(u'[\t\n\x0b\x0c\r\x00]+', ' ', q)
        q = q.strip()
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
                    res = {'success': False,
                           'error': 'genomic interval query cannot be combined with "species=all" parameter. Specify a single species.'}
                    if is_async:
                        callback(res)
                        return
                    else:
                        return res

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
        except MGQueryError as err:
            res = {'success': False,
                   'error': err.message}
            if is_async:
                callback(res)
                return
            else:
                return res

        if _q:
            if options.rawquery:
                if is_async:
                    callback(_q)
                    return
                else:
                    return _q

            if is_async:
                def inner_callback(response):
                    res = json.loads(response.body)
                    if not options.raw:
                        res = self._normalize_query_res(res, options)
                    callback(res)
                self._search_async(_q, species=kwargs['species'], callback=inner_callback)
                return
            else:
                try:
                    res = self._search(_q, species=kwargs['species'])
                    if not options.raw:
                        res = self._normalize_query_res(res, options)
                except ElasticSearchException as err:
                    err_msg = err.message if options.raw else "invalid query term."
                    res = {'success': False,
                           'error': err_msg}
        else:
            res = {'success': False, 'error': "Invalid query. Please check parameters."}

        if is_async:
            callback(res)
            return
        else:
            return res
