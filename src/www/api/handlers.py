# -*- coding: utf-8 -*-
from biothings.www.api.es.handlers import BiothingHandler
from biothings.www.api.es.handlers import MetadataHandler
from biothings.www.api.es.handlers import QueryHandler
from biothings.www.api.es.handlers import StatusHandler
from tornado.web import RequestHandler

class GeneHandler(BiothingHandler):
    ''' This class is for the /gene endpoint. '''
    pass

class QueryHandler(QueryHandler):
    ''' This class is for the /query endpoint. '''
    pass

class StatusHandler(StatusHandler):
    ''' This class is for the /status endpoint. '''
    pass

class MetadataHandler(MetadataHandler):
    ''' This class is for the /metadata endpoint. '''
    pass

class TaxonHandler(RequestHandler):
    def get(self, taxid):
        self.redirect("http://t.biothings.io/v1/taxon/%s?include_children=1" % taxid)

class DemoHandler(RequestHandler):
    def get(self):
        with open('../docs/demo/index.html', 'r') as demo_file: 
            self.write(demo_file.read())
    
