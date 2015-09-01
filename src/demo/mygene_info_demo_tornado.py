# Copyright [2013-2014] [Chunlei Wu]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
if sys.version > '3':
    PY3 = True
else:
    PY3 = False

if PY3:
    import urllib.request, urllib.parse, urllib.error
    import http.client
else:
    import urllib
    import httplib
import types
import json


import tornado.httpserver
import tornado.ioloop
import tornado.web


def call_service(url):
    if PY3:
        h = http.client.HTTPConnection('mygene.info')
    else:
        h = httplib.HTTPConnection('mygene.info')
    h.request('GET', url)
    res = h.getresponse()
    con = res.read()
    if res.status == 200:
        out = json.loads(con)
        return out

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        d = {'gene_list': None, 'ps_list': None, 'error': None}
        query = self.get_argument('q', '')
        if query:
            if PY3:
                out = call_service('/v2/query?' + urllib.parse.urlencode(dict(q=query, species='mouse', limit=1000)))
            else:
                out = call_service('/v2/query?' + urllib.urlencode(dict(q=query, species='mouse', limit=1000)))
            if 'total' in out:
                gene_list = []
                for gene in out['hits']:
                    gene_list.append({'id': gene['_id'],
                                      'symbol': gene.get('symbol', 'None'),
                                      'name': gene.get('name', '')})
                d['gene_list']=gene_list
            else:
                d['error'] = out.get('error', out.get('reason', 'Invalid query!'))
        else:
           geneid = self.get_argument('showgene', '')
           if geneid:
               #show gene page
               gene = call_service('/v2/gene/%s?fields=reporter' % geneid)
               ps_list = []
               if gene and 'reporter' in gene:
                   ps_list = gene['reporter'].get('Mouse430_2',[])
                   if PY3:
                       if type(ps_list) is not list:
                           # if only one probeset available, it's returned as a string, so we need to convert it to a list
                           ps_list = [ps_list]
                   else:
                       if type(ps_list) is not types.ListType:
                           # if only one probeset available, it's returned as a string, so we need to convert it to a list
                           ps_list = [ps_list]
               d['ps_list'] = ps_list
        self.render('templates/demo_form.html', **d)

def main():
    application = tornado.web.Application([(r"/", MainHandler)])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8000, address='127.0.0.1')
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
