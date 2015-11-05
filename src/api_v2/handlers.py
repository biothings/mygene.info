import re
import json

from tornado.web import HTTPError

from helper import BaseHandler
from utils.es import ESQuery
from utils.taxonomy import TaxonomyQuery
from utils.common import split_ids
import os


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
                raise HTTPError(404)
        else:
            raise HTTPError(404)

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
            kwargs.setdefault('species', 'all')
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
            fetch_all

            explain
        '''
        kwargs = self.get_query_params()
        q = kwargs.pop('q', None)
        scroll_id = kwargs.pop('scroll_id', None)
        _has_error = False
        if scroll_id:
            res = self.esq.scroll(scroll_id, fields=None, **kwargs)
        elif q:
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
                if kwargs.get('fetch_all', False):
                    self.ga_track(event={'category': 'v2_api',
                                         'action': 'fetch_all',
                                         'label': 'total',
                                         'value': res.get('total', None)})
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

            jsoninput   if true, input "q" is a json string, must be decoded as a list.
        '''
        kwargs = self.get_query_params()
        q = kwargs.pop('q', None)
        jsoninput = kwargs.pop('jsoninput', None) in ('1', 'true')
        if q:
            # ids = re.split('[\s\r\n+|,]+', q)
            try:
                ids = json.loads(q) if jsoninput else split_ids(q)
                if not isinstance(ids, list):
                    raise ValueError
            except ValueError:
                ids = None
                res = {'success': False, 'error': 'Invalid input for "q" parameter.'}
            if ids:
                scopes = kwargs.pop('scopes', None)
                fields = kwargs.pop('fields', None)
                res = self.esq.mget_gene2(ids, fields=fields, scopes=scopes, **kwargs)
        else:
            res = {'success': False, 'error': "Missing required parameters."}

        self.return_json(res)
        self.ga_track(event={'category': 'v2_api',
                             'action': 'query_post',
                             'label': 'qsize',
                             'value': len(q) if q else 0})


class SpeciesHandler(BaseHandler):
    tq = TaxonomyQuery()

    def get(self, taxid):
        kwargs = self.get_query_params()
        include_children = kwargs.get('include_children', False)
        has_gene = kwargs.get('has_gene', False)
        res = self.tq.get_species_info(taxid, include_children=include_children, has_gene=has_gene)
        if res:
            self.return_json(res)
        else:
            raise HTTPError(404)


class MetaDataHandler(BaseHandler):
    '''Return db metadata in json string.'''
    disable_caching = True

    def get(self):
        esq = ESQuery()
        metadata = esq.metadata()
        metadata["app_revision"] = os.environ["MYGENE_REVISION"]
        self.return_json(metadata, indent=2)


class FieldsHandler(BaseHandler):
    esq = ESQuery()

    def get(self):
        #notes = json.load(open(config.FIELD_NOTES_PATH, 'r'))
        es_mapping = self.esq.query_fields()

        def get_indexed_properties_in_dict(d, prefix):
            r = {}
            for (k, v) in d.items():
                r[prefix + '.' + k] = {}
                r[prefix + '.' + k]['indexed'] = False
                if 'type' in v:
                    r[prefix + '.' + k]['type'] = v['type']
                    if ('index' not in v) or ('index' in v and v['index'] != 'no'):
                        # indexed field
                        r[prefix + '.' + k]['indexed'] = True
                else:
                    r[prefix + '.' + k]['type'] = 'object'
                    r.update(get_indexed_properties_in_dict(v['properties'], prefix + '.' + k))
            return r

        r = {}
        for (k, v) in get_indexed_properties_in_dict(es_mapping, '').items():
            k1 = k.lstrip('.')
            r[k1] = v
            #if k1 in notes:
            #    r[k1]['notes'] = notes[k1]
        self.return_json(r)


APP_LIST = [
    (r"/gene/([\w\-\.]+)/?", GeneHandler),   # for gene get request
    (r"/gene/?$", GeneHandler),              # for gene post request
    (r"/query/?", QueryHandler),
    (r"/species/(\d+)/?", SpeciesHandler),
    (r"/metadata", MetaDataHandler),
    (r"/metadata/fields", FieldsHandler),
]
