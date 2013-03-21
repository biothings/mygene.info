'''
A thin python layer for accessing GeneDoc ElasticSearch host.

Currently available URLs:

    /query?q=cdk2      gene query service
    /gene/<geneid>     gene annotation service

'''
import sys
import os.path
import subprocess
import json
import re

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.escape
from tornado.options import define, options

src_path = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
if src_path not in sys.path:
    sys.path.append(src_path)
from utils.es import ESQuery
from helper import BaseHandler

__USE_WSGI__ = False

define("port", default=8000, help="run on the given port", type=int)
define("address", default="127.0.0.1", help="run on localhost")
define("debug", default=False, type=bool, help="run in debug mode")
tornado.options.parse_command_line()
if options.debug:
    import tornado.autoreload
    import logging
    logging.getLogger().setLevel(logging.DEBUG)
    options.address = '0.0.0.0'


def _get_rev():
    '''return current mercurial rev number.
        e.g.
           72:a8ef9f842af7
    '''
    pipe = subprocess.Popen(["hg", "id", "-n", "-i"],
                            stdout=subprocess.PIPE)
    output = pipe.stdout.read().strip()
    return ':'.join(reversed(output.replace('+', '').split(' ')))
__revision__ = _get_rev()


class StatusCheckHandler(tornado.web.RequestHandler):
    '''This reponses to a HEAD request of /status for status check.'''
    def head(self):
        esq = ESQuery()
        esq.get_gene2('1017')

    def get(self):
        self.head()
        self.write('OK')


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('templates/index.html')


"""
class MetaDataHandler(tornado.web.RequestHandler):
    '''Return db metadata in json string.'''
    def get(self):
        bs = BoCServiceLayer()
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        metadata = bs.get_metadata(raw=True)
        metadata = '{"app_revision": "%s",' % __revision__ + metadata[1:]
        self.write(metadata)
"""

class GeneHandler(BaseHandler):
    esq = ESQuery()

    def get(self, geneid=None):
        '''/gene/<geneid>
           geneid can be entrezgene, ensemblgene, retired entrezgene ids.
           /gene/1017
           /gene/1017?filter=symbol,name
           /gene/1017?filter=symbol,name,reporter.HG-U133_Plus_2
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
            self.return_json(res)


class IntervalQueryHandler(tornado.web.RequestHandler):
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
            _json_data = json.dumps(res)
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            self.write(_json_data)


APP_LIST = [
        (r"/", MainHandler),
        (r"/status", StatusCheckHandler),
#        (r"/metadata", MetaDataHandler),
        (r"/gene/([\w\-\.]+)/?", GeneHandler),   #for get request
        (r"/gene/?", GeneHandler),               #for post request
        (r"/query/?", QueryHandler),
        (r"/interval/?", IntervalQueryHandler),
]

settings = {}
# if options.debug:
#     from config import STATIC_PATH
#     settings.update({
#         "static_path": STATIC_PATH,
# #        "cookie_secret": COOKIE_SECRET,
# #        "login_url": LOGIN_URL,
# #        "xsrf_cookies": True,
#     })


def main():
    application = tornado.web.Application(APP_LIST, **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port, address=options.address)
    loop = tornado.ioloop.IOLoop.instance()
    if options.debug:
        tornado.autoreload.start(loop)
        logging.info('Server is running on "%s:%s"...' % (options.address, options.port))

    loop.start()

if __USE_WSGI__:
    import tornado.wsgi
    wsgi_app = tornado.wsgi.WSGIApplication(APP_LIST)


if __name__ == "__main__":
    main()

