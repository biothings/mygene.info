import json
import re
import tornado.web

from helper import BaseHandler
from utils.es import ESQuery

#GeneHandler is the same as the v2
from api_v2.handlers import GeneHandler


class QueryHandler(BaseHandler):
    esq = ESQuery()


    def _homologene_trimming(self, gdoc_li):
        '''A special step to remove species not included in <species_li>
           from "homologene" attributes.
           species_li is a list of taxids
        '''
        #do homologene trimming for nine species v1 mygene.info supports.
        species_li = [9606, 10090, 10116, 7227, 6239, 7955, 3702, 8364, 9823]
        species_set = set(species_li)
        for idx, gdoc in enumerate(gdoc_li):
            if gdoc:
                hgene = gdoc.get('homologene', None)
                if hgene:
                    _genes = hgene.get('genes', None)
                    if _genes:
                        _genes_filtered = [g for g in _genes if g[0] in species_set]
                        hgene['genes'] = _genes_filtered
                        gdoc['homologene'] = hgene
                        gdoc_li[idx] = gdoc
        return gdoc_li

    def get(self):
        """
        allowed parameters:
              q
              skip
              limit
              sort
              callback
        """
        kwargs = self.get_query_params()
        q = kwargs.pop('q', None)
        if q:
            size = kwargs.pop('limit', None)
            kwargs['size'] = int(size) if size else 25   #default size set to 25
            _from = kwargs.pop('skip', None)
            if _from:
                kwargs['from'] = int(_from)
            kwargs['fields'] = ['symbol','name','taxid', 'homologene']
            res = self.esq.query(q, **kwargs)
            #re-format res to make it a v1 compatible
            res['total_rows'] = res['total']
            res['skip'] = kwargs['from'] if _from else 0
            res['limit'] = kwargs['size']
            res['rows'] = self._homologene_trimming(res['hits'])
            for hit in res['rows']:
                hit['score'] = hit['_score']
                hit['id'] = hit['_id']
                del hit['_score']
                del hit['_id']
            res['etag'] = str(hex(hash(str(res['rows']))))[2:]

            del res['total']
            del res['hits']
            self.return_json(res)

    def post(self):
        '''
        parameters:
            q
            scope
        '''
        kwargs = self.get_query_params()
        q = kwargs.pop('q', None)
        if q:
            ids = re.split('[\s\r\n+|,]+', q)
            scopes = kwargs.pop('scope', None)
            if scopes:
                scopes = [x.strip() for x in scopes.split(',')]
            kwargs['scopes'] = scopes
            fields = ['symbol','name','taxid', 'homologene']
            kwargs['fields'] = fields
            res = self.esq.mget_gene2(ids, **kwargs)
            res = self._homologene_trimming(res)
            for hit in res:
                if hit and '_id' in hit:
                    hit['id'] = hit['_id']
                    del hit['_id']

            self.return_json({'rows': res})

APP_LIST = [

        (r"/gene/([\w\-\.]+)/?", GeneHandler),   #for get request
        (r"/gene/?", GeneHandler),               #for post request
        (r"/query/?", QueryHandler),


]
