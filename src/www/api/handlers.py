import re
import json

from tornado.web import HTTPError
from biothings.www.api.handlers import MetaDataHandler, BiothingHandler, QueryHandler, \
                                       FieldsHandler, BaseHandler

from biothings.utils.version import get_software_info
from biothings.settings import BiothingSettings
from utils.es import ESQuery
from biothings.utils.common import split_ids
from config import GA_EVENT_CATEGORY
import os, logging

mygene_settings = BiothingSettings()


class MyGeneMetaDataHandler(MetaDataHandler):
    '''Return db metadata in json string.'''
    disable_caching = True
    esq = ESQuery()

    def get(self):
        _meta = self.esq.metadata()
        self._fill_software_info(_meta)
        _meta["app_revision"] = os.environ["MYGENE_REVISION"]
        self.return_json(_meta, indent=2)

class MyGeneFieldsHandler(FieldsHandler):
    ''' This class is for the /metadata/fields endpoint. '''
    esq = ESQuery()

class GeneHandler(BiothingHandler):
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
            gene = self.esq.get_gene(geneid, **kwargs)
            if gene:
                self.return_json(gene)
                self.ga_track(event={'category': GA_EVENT_CATEGORY,
                                     'action': 'gene_get'})
            else:
                raise HTTPError(404)
        else:
            raise HTTPError(404)


class QueryHandler(QueryHandler):
    esq = ESQuery()

    # over ride from biothings BaseHandler to stop renaming "from" to "from_"
    def _check_paging_param(self, kwargs):
        '''support paging parameters, limit and skip as the aliases of size and from.'''
        if 'limit' in kwargs and 'size' not in kwargs:
            kwargs['size'] = kwargs['limit']
            del kwargs['limit']
        if 'skip' in kwargs and 'from' not in kwargs:
            kwargs['from'] = kwargs['skip']
            del kwargs['skip']
        # cap size
        if 'size' in kwargs:
            cap = mygene_settings.size_cap
            try:
                kwargs['size'] = int(kwargs['size']) > cap and cap or kwargs['size']
            except ValueError:
                # int conversion failure is delegated to later process
                pass
        return kwargs

class TaxonHandler(BaseHandler):

    def get(self, taxid):
        self.redirect("http://t.biothings.io/v1/taxon/%s?include_children=1" % taxid)


APP_LIST = [
    (r"/gene/([\w\-\.]+)/?", GeneHandler),   # for gene get request
    (r"/gene/?$", GeneHandler),              # for gene post request
    (r"/query/?", QueryHandler),
    (r"/species/(\d+)/?", TaxonHandler),
    (r"/taxon/(\d+)/?", TaxonHandler),
    (r"/metadata", MyGeneMetaDataHandler),
    (r"/metadata/fields", MyGeneFieldsHandler),
]
