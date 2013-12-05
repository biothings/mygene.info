import re
import tornado.web

from helper import BaseHandler
from utils.es import ESQuery
from utils.common import split_ids


class GeneHandler(BaseHandler):
    esq = ESQuery()

    def get(self, geneid=None):
        '''/gene/<geneid>
           geneid can be entrezgene, ensemblgene, retired entrezgene ids.
           /gene/1017
           /gene/1017?fields=symbol,name
           /gene/1017?fields=symbol,name,reporter.HG-U133_Plus_2
        '''
        if geneid:
            kwargs = self.get_query_params()
            kwargs.setdefault('scopes', 'entrezgene,ensemblgene,retired')
            kwargs.setdefault('species', 'all')
            gene = self.esq.get_gene2(geneid, **kwargs)
            if gene:
                self.return_json(gene)
                self.ga_track(event={'category': 'v2_api',
                                     'action': 'gene_get'})
            else:
                raise tornado.web.HTTPError(404)
        else:
            raise tornado.web.HTTPError(404)

    def post(self, geneid=None):
        '''
           This is essentially the same as post request in QueryHandler, with different defaults.

           parameters:
            ids
            fields
            species
        '''
        kwargs = self.get_query_params()
        ids = kwargs.pop('ids', None)
        if ids:
            ids = re.split('[\s\r\n+|,]+', ids)
            scopes = 'entrezgene,ensemblgene,retired'
            fields = kwargs.pop('fields', None)
            res = self.esq.mget_gene2(ids, fields=fields, scopes=scopes, **kwargs)
        else:
            res = {'success': False, 'error': "Missing required parameters."}

        self.return_json(res)
        self.ga_track(event={'category': 'v2_api',
                             'action': 'gene_post',
                             'label': 'qsize',
                             'value': len(ids) if ids else 0})


class QueryHandler(BaseHandler):
    esq = ESQuery()

    def get(self):
        '''
        parameters:
            q
            fields
            from
            size
            sort
            species

            explain
        '''
        kwargs = self.get_query_params()
        q = kwargs.pop('q', None)
        _has_error = False
        if q:
            explain = self.get_argument('explain', None)
            if explain and explain.lower() == 'true':
                kwargs['explain'] = True
            for arg in ['from', 'size', 'mode']:
                value = kwargs.get(arg, None)
                if value:
                    try:
                        kwargs[arg] = int(value)
                    except ValueError:
                        res = {'success': False, 'error': 'Parameter "{}" must be an integer.'.format(arg)}
                        _has_error = True
            if not _has_error:
                res = self.esq.query(q, **kwargs)
        else:
            res = {'success': False, 'error': "Missing required parameters."}

        self.return_json(res)
        self.ga_track(event={'category': 'v2_api',
                             'action': 'query_get',
                             'label': 'qsize',
                             'value': len(q) if q else 0})

    def post(self):
        '''
        parameters:
            q
            scopes
            fields
            species
        '''
        kwargs = self.get_query_params()
        q = kwargs.pop('q', None)
        if q:
            # ids = re.split('[\s\r\n+|,]+', q)
            try:
                ids = split_ids(q)
            except ValueError:
                ids = None
                res = {'success': False, 'error': 'Invalid input for "q" parameter.'}
            if ids:
                scopes = kwargs.pop('scopes', None)
                if scopes:
                    scopes = [x.strip() for x in scopes.split(',')]
                fields = kwargs.pop('fields', None)
                res = self.esq.mget_gene2(ids, fields=fields, scopes=scopes, **kwargs)
        else:
            res = {'success': False, 'error': "Missing required parameters."}

        self.return_json(res)
        self.ga_track(event={'category': 'v2_api',
                             'action': 'query_post',
                             'label': 'qsize',
                             'value': len(q) if q else 0})


APP_LIST = [
    (r"/gene/([\w\-\.]+)/?", GeneHandler),   # for gene get request
    (r"/gene/?$", GeneHandler),              # for gene post request
    (r"/query/?", QueryHandler),
]
