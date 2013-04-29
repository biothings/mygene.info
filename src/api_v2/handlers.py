import json
import re
import tornado.web

from helper import BaseHandler
from utils.es import ESQuery


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
            else:
                raise tornado.web.HTTPError(404)
        else:
            raise tornado.web.HTTPError(404)


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
        if q:
            explain = self.get_argument('explain', None)
            if explain and explain.lower()=='true':
                kwargs['explain'] = True
            for arg in ['from', 'size', 'mode']:
                value = kwargs.get(arg, None)
                if value:
                    kwargs[arg] = int(value)
            res = self.esq.query(q, **kwargs)
        else:
            res = {'success': False, 'error': "Missing required parameters."}

        self.return_json(res)


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
            ids = re.split('[\s\r\n+|,]+', q)
            scopes = kwargs.pop('scopes', None)
            if scopes:
                scopes = [x.strip() for x in scopes.split(',')]
            fields = kwargs.pop('fields', None)
            res = self.esq.mget_gene2(ids, fields=fields, scopes=scopes, **kwargs)
        else:
            res = {'success': False, 'error': "Missing required parameters."}

        self.return_json(res)


APP_LIST = [

        (r"/gene/([\w\-\.]+)/?", GeneHandler),   #for get request
        (r"/query/?", QueryHandler),

]
