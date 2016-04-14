import re
import json

from biothings.www.api.handlers import MetaDataHandler, BiothingHandler, QueryHandler, \
                                       FieldsHandler, BaseHandler
from biothings.settings import BiothingSettings
from utils.es import ESQuery
from biothings.utils.common import split_ids
import os, logging

mygene_settings = BiothingSettings()


class MyGeneMetaDataHandler(MetaDataHandler):
    '''Return db metadata in json string.'''
    disable_caching = True
    esq = ESQuery()

    def get(self):
        metadata = self.esq.metadata()
        metadata["app_revision"] = os.environ["MYGENE_REVISION"]
        self.return_json(metadata, indent=2)

class MyGeneFieldsHandler(FieldsHandler):
    ''' This class is for the /metadata/fields endpoint. '''
    esq = ESQuery()


class GeneHandler(BiothingHandler):
    esq = ESQuery()


class QueryHandler(QueryHandler):
    esq = ESQuery()


class SpeciesHandler(BaseHandler):

    def get(self, taxid):
        self.redirect("http://s.biothings.io/v1/species/%s?include_children=1" % taxid)


APP_LIST = [
    (r"/gene/([\w\-\.]+)/?", GeneHandler),   # for gene get request
    (r"/gene/?$", GeneHandler),              # for gene post request
    (r"/query/?", QueryHandler),
    (r"/species/(\d+)/?", SpeciesHandler),
    (r"/metadata", MyGeneMetaDataHandler),
    (r"/metadata/fields", MyGeneFieldsHandler),
]
