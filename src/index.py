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
from helper import add_apps, BaseHandler
from api_v1.handlers import APP_LIST as api_v1_app_list
from api_v2.handlers import APP_LIST as api_v2_app_list
from api_v2.handlers_async import APP_LIST as api_v2_async_app_list
from demo.handlers import APP_LIST as demo_app_list
#from auth.handlers import APP_LIST as auth_app_list

__USE_WSGI__ = False
DOCS_STATIC_PATH = os.path.join(src_path, 'docs/_build/html')
if not os.path.exists(DOCS_STATIC_PATH):
    raise IOError('Run "make html" to generate sphinx docs first.')
STATIC_PATH = os.path.join(src_path, 'src/static')

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
        #self.redirect('/index.html')
        self.render(os.path.join(DOCS_STATIC_PATH, 'index.html'))


class MetaDataHandler(BaseHandler):
    '''Return db metadata in json string.'''
    def get(self):
        esq = ESQuery()
        metadata = esq.metadata()
        metadata["app_revision"] = __revision__
        self.return_json(metadata)


APP_LIST = [
        (r"/", MainHandler),
        (r"/status", StatusCheckHandler),
        (r"/metadata", MetaDataHandler),
        (r"/v2/metadata", MetaDataHandler),
        (r"/v2a/metadata", MetaDataHandler),
]

APP_LIST += add_apps('', api_v2_app_list)
APP_LIST += add_apps('v2', api_v2_app_list)
APP_LIST += add_apps('v1', api_v1_app_list)
APP_LIST += add_apps('demo', demo_app_list)

APP_LIST += add_apps('v2a', api_v2_async_app_list)
#APP_LIST += add_apps('auth', auth_app_list)
if options.debug:
    APP_LIST += [
            #/widget/* static path
            (r"/widget/(.*)", tornado.web.StaticFileHandler, {'path': os.path.join(STATIC_PATH, 'widget')}),
            #this should be the last one
            (r"/?(.*)", tornado.web.StaticFileHandler, {'path': DOCS_STATIC_PATH}),
    ]

settings = {}
if options.debug:
#     from config import STATIC_PATH
    settings.update({
         "static_path": STATIC_PATH,
     })
#    from config import auth_settings
#    settings.update(auth_settings)

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

