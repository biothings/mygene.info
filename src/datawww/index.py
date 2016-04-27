'''
A thin python layer for accessing GeneDoc MongoDB

Currently available URLs:

    /                  main page, redirected to /doc for now

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
# from dataindex import ESQuery
# from helper import BaseHandler

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
    '''return current git rev number.
        e.g.
           9d9811e21a878bed4c8d7de5ab20bf0baa5aa87f
    '''
    pipe = subprocess.Popen(["git", "rev-parse", "HEAD"],
                            stdout=subprocess.PIPE)
    output = pipe.stdout.read().strip()
    print(output)
    return ':'.join(reversed(output.replace('+', '').split(' ')))
__revision__ = _get_rev()

"""
class StatusCheckHandler(tornado.web.RequestHandler):
    '''This reponses to a HEAD request of /status for status check.'''
    def head(self):
        bs = BoCServiceLayer()
        bs.get_genedoc('1017')

    def get(self):
        self.head()


class MetaDataHandler(tornado.web.RequestHandler):
    '''Return db metadata in json string.'''
    def get(self):
        bs = BoCServiceLayer()
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        metadata = bs.get_metadata(raw=True)
        metadata = '{"app_revision": "%s",' % __revision__ + metadata[1:]
        self.write(metadata)


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
            # fields = kwargs.get('fields', None)
            explain = self.get_argument('explain', None)
            if explain and explain.lower() == 'true':
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
            if explain and explain.lower() == 'true':
                kwargs['explain'] = True
            for arg in ['from', 'size', 'mode']:
                value = self.get_argument(arg, None)
                if value:
                    kwargs[arg] = int(value)
            # sample = self.get_argument('sample', None) == 'true'
            esq = ESQuery()
            res = esq.query_interval(**kwargs)
            _json_data = json.dumps(res)
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            self.write(_json_data)

"""

class MongoViewer(tornado.web.RequestHandler):
    def get(self, db, collection=None, id=None):
        import random
        from utils.mongo import get_src_conn

        get_random = self.get_argument('random', None) != 'false'
        size = int(self.get_argument('size', 10))

        conn = get_src_conn()
        if collection:
            if collection == 'fs':
                import gridfs
                fs = gridfs.GridFS(conn[db])
                out = fs.list()
            else:
                collection = conn[db][collection]
                if id:
                    out = collection.find_one({"_id": id})
                elif get_random:
                    cnt = collection.count()
                    num = random.randint(0, max(cnt-size, 0))
                    out = list(collection.find().skip(num).limit(size))
                else:
                    out = list(collection.find().limit(size))
        else:
            #list all collection in this db
            out = conn[db].collection_names()

        def date_handler(obj):
            return obj.isoformat() if hasattr(obj, 'isoformat') else obj
        _json_data = json.dumps(out, default=date_handler)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(_json_data)


class LogViewer(tornado.web.RequestHandler):
    def get(self, kind, src, timestamp=None):
        dump_dir = '/opt/genedoc-hub/load_archive/by_resources/'
        build_dir = '/home/cwu/prj/genedoc-hub/logs/'
        logfile = None
        if kind in ['dump', 'upload']:
            dir_base = dump_dir + src
            if os.path.exists(dir_base):
                if not timestamp:
                    timestamp = timestamp or sorted(os.walk(dir_base).next()[1])[-1]
                if src == 'ucsc':
                    timestamp = ''
                logfile = os.path.join(dir_base, timestamp,
                                       src + ('_dump.log' if kind == 'dump' else '_upload.log'))
        elif kind in ['build', 'sync']:
            if kind == 'build':
                _prefix = 'databuild_genedoc'
            elif kind == 'sync':
                _prefix = 'databuild_sync_genedoc'
            if timestamp:
                logfile = os.path.join(build_dir, '{}_{}_{}.log'.format(_prefix, src, timestamp))
            else:
                logfile = sorted([fn for fn in os.walk(build_dir).next()[2] if re.match('{}_{}_\d+.log'.format(_prefix, src), fn)])[-1]
                logfile = os.path.join(build_dir, logfile)

        if logfile and os.path.exists(logfile):
            with file(logfile) as log_f:
                self.write('<pre>')
                self.write(log_f.read())
                self.write('</pre>')
        else:
            self.write("Not found: {}".format(logfile))


APP_LIST = [
    #    (r"/status", StatusCheckHandler),
    #    (r"/metadata", MetaDataHandler),
    #    (r"/release_notes", ReleaseNotesHandler),
    #(r"/gene/([\w\-\.]+)/?", GeneHandler),   # for get request
    #(r"/gene/?", GeneHandler),               # for post request
    #(r"/query/?", QueryHandler),
    #(r"/interval/?", IntervalQueryHandler),
    (r"/mongo/(\w+)/?(\w*)/?(\w*)/?", MongoViewer),
    (r"/log/(\w+)/(\w+)/?(\w*)/?", LogViewer),
]

settings = {}
# if options.debug:
#     from boccfg import STATIC_PATH
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
