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

import config

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
    output = pipe.stdout.read().strip().decode()
    print(output)
    return ':'.join(reversed(output.replace('+', '').split(' ')))
__revision__ = _get_rev()


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
                    num = random.randint(0, max(cnt - size, 0))
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
        dump_dir = os.path.join(config.DATA_ARCHIVE_ROOT,"by_resources")
        build_dir = config.LOG_FOLDER
        logfile = None
        if kind in ['dump', 'upload']:
            dir_base = os.path.join(dump_dir,src)
            if os.path.exists(dir_base):
                if not timestamp:
                    timestamp = timestamp or sorted(next(os.walk(dir_base))[1])[-1]
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
                logfile = sorted([fn for fn in next(os.walk(build_dir))[2] if re.match('{}_{}_\d+.log'.format(_prefix, src), fn)])[-1]
                logfile = os.path.join(build_dir, logfile)

        if logfile and os.path.exists(logfile):
            with open(logfile) as log_f:
                self.write('<pre>')
                self.write(log_f.read())
                self.write('</pre>')
        else:
            self.write("Not found: {}".format(logfile))


APP_LIST = [
    (r"/mongo/(\w+)/?(\w*)/?(\w*)/?", MongoViewer),
    (r"/log/(\w+)/(\w+)/?(\w*)/?", LogViewer),
]

settings = {}

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
