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
            gene = self.esq.get_gene2(geneid, **kwargs)
            self.return_json(gene)
        else:
            raise tornado.web.HTTPError(404)

    def post(self):
        '''
           post to /gene

           with parameters of
            {'ids': '1017,1018',
             'filter': 'symbol,name'}

            {'ids': '1017',
             'filter': 'symbol,name,reporter.HG-U133_Plus_2'}
        '''
        kwargs = self.get_query_params()
        geneids = kwargs.pop('ids', None)
        if geneids:
            geneids = [_id.strip() for _id in geneids.split(',')]
            res = self.esq.mget_gene2(geneids, **kwargs)
            self.return_json(res)
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

            explain
            sample
        '''
        kwargs = self.get_query_params()
        q = kwargs.pop('q', None)
        if q:
            #fields = kwargs.get('fields', None)
            explain = self.get_argument('explain', None)
            if explain and explain.lower()=='true':
                kwargs['explain'] = True
            for arg in ['from', 'size', 'mode']:
                value = kwargs.get(arg, None)
                if value:
                    kwargs[arg] = int(value)
            sample = kwargs.get('sample', None) == 'true'

            if sample:
                res = self.esq.query_sample(q, **kwargs)
            else:
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



class IntervalQueryHandler(BaseHandler):
    def get(self):
        #/interval?interval=chr12:56350553-56367568&taxid=9606
        interval = self.get_argument('interval', None)
        taxid = self.get_argument('taxid', None)
        kwargs = {}
        if interval and taxid:
            kwargs['taxid'] = int(taxid)
            pattern = r'chr(?P<chr>\w+):(?P<gstart>[0-9,]+)-(?P<gend>[0-9,]+)'
            mat = re.search(pattern, interval)
            if mat:
                kwargs.update(mat.groupdict())
            fields = self.get_argument('fields', None)
            if fields:
                fields = fields.split(',')
                kwargs['fields'] = fields
            explain = self.get_argument('explain', None)
            if explain and explain.lower()=='true':
                kwargs['explain'] = True
            for arg in ['from', 'size', 'mode']:
                value = self.get_argument(arg, None)
                if value:
                    kwargs[arg] = int(value)
            #sample = self.get_argument('sample', None) == 'true'
            esq = ESQuery()
            res = esq.query_interval(**kwargs)
            self.return_json(res)


APP_LIST = [

        (r"/gene/([\w\-\.]+)/?", GeneHandler),   #for get request
        (r"/gene/?", GeneHandler),               #for post request
        (r"/query/?", QueryHandler),
        (r"/interval/?", IntervalQueryHandler),

]
