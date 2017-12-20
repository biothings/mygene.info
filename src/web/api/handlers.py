# -*- coding: utf-8 -*-
from biothings.web.api.es.handlers import BiothingHandler
from biothings.web.api.es.handlers import MetadataHandler
from biothings.web.api.es.handlers import QueryHandler
from biothings.web.api.es.handlers import StatusHandler
from biothings.utils.version import get_repository_information
from tornado.web import RequestHandler
from collections import OrderedDict
import requests
import os

#import logging

def get_es_index(inst, options):
    return inst.web_settings.ES_INDEX
    #if 'all' in options.esqb_kwargs.species or len(set(options.esqb_kwargs.species)-
    #    set([x['tax_id'] for x in inst.web_settings.TAXONOMY.values()])) > 0:
    #    return inst.web_settings.ES_INDEX
    #else:
    #    return inst.web_settings.ES_INDEX_TIER1

class FrontPageHandler(BiothingHandler):
    def get(self):
        self.write("MYGENE FRONTPAGE!")

class GeneHandler(BiothingHandler):
    ''' This class is for the /gene endpoint. '''
    def _get_es_index(self, options):
        return get_es_index(self, options)

class QueryHandler(QueryHandler):
    ''' This class is for the /query endpoint. '''
    def _pre_query_builder_GET_hook(self, options):
        if options.esqb_kwargs.include_tax_tree and 'all' not in options.esqb_kwargs.species:
            headers = {'content-type': 'application/x-www-form-urlencoded',
                        'user-agent': 'Python-requests_mygene.info/{} (gzip)'.format(requests.__version__)}

            res = requests.post(self.web_settings.INCLUDE_TAX_TREE_REDIRECT_TEMPLATE.format(
                ids=','.join(['{}'.format(sid) for sid in options.esqb_kwargs.species])), headers=headers)

            if res.status_code == requests.codes.ok:
                options['esqb_kwargs']['species'] = [str(x) for x in res.json()]
                #logging.debug('tax_tree species: {}'.format(options.esqb_kwargs.species))

        return options

    def _get_es_index(self, options):
        return get_es_index(self, options)

class StatusHandler(StatusHandler):
    ''' This class is for the /status endpoint. '''
    pass

class MetadataHandler(MetadataHandler):
    ''' This class is for the /metadata endpoint. '''
    def _pre_finish_GET_hook(self, options, res):
        if not self.request.path.endswith('fields'):
            # Add mygene specific metadata stuff
            res['available_fields'] = 'http://mygene.info/metadata/fields'
            res['app_revision'] = get_repository_information(app_dir=self.web_settings._app_git_repo).get('commit-hash', '')
            res['genome_assembly'] = {}
            res['taxonomy'] = {}
            for (s, d) in self.web_settings.TAXONOMY.items():
                if 'tax_id' in d:
                    res['taxonomy'][s] = int(d['tax_id'])
                if 'assembly' in d:
                    res['genome_assembly'][s] = d['assembly']
            if "source" not in res:
                # occurs when loaded from scratch, not from a change/diff file
                res["source"] = None
            res = OrderedDict(sorted(list(res.items()), key=lambda x: x[0]))
        return res

class TaxonHandler(RequestHandler):
    def initialize(self, web_settings):
        pass

    def get(self, taxid):
        self.redirect("http://t.biothings.io/v1/taxon/%s?include_children=1" % taxid)

class DemoHandler(RequestHandler):
    def initialize(self, web_settings):
        pass

    def get(self):
        with open('../docs/demo/index.html', 'r') as demo_file: 
            self.write(demo_file.read())
