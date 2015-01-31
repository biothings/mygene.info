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


#!/usr/bin/python
print("Content-Type: text/html")

import os
import cgi
try:
    import urlparse
    import urllib
    import httplib
    PY3=False
except ImportError:
    import urllib.parse
    import urllib.request, urllib.parse, urllib.error
    import http.client
    PY3=True
import types
import json

#turn it on when debugging
#import cgitb
#cgitb.enable()

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
    else:
        print(con)


form_html = '''
<html>
<form action="", method="GET">
<p style="text-align:left"><label>Search for genes:</label>
<input type="text" name="q" style="width:200px"></input>
<input type="hidden" name="limit" value="100" /><input type="submit"></input></p>
</form>
'''
print(form_html)

qs = os.environ.get("QUERY_STRING", '')
if  PY3:
    params = urllib.parse.parse_qs(qs)
else:
    params = urlparse.parse_qs(qs)
query = params.get('q', [''])[0]
if query:
    #do the query
    if PY3:
        out = call_service('/v2/query?' + urllib.parse.urlencode(dict(q=query, species='mouse', limit=1000)))
    else:
        out = call_service('/v2/query?' + urllib.urlencode(dict(q=query, species='mouse', limit=1000)))
    if 'total' in out:
        #render the gene list
        print("<h3>Found %d matched mouse gene(s)</h3>" % out['total'])
        if out['total']>0:
            print('<table>')
            print('<tr><td>Symbol</td><td>Name</td></td>')
            for gene in out['hits']:
                print('<tr><td><a href="?showgene=%s">%s</a></td><td>%s</td></tr>' % (gene['_id'], gene.get('symbol', 'None'), gene.get('name', '')))
            print('</table>')
    else:
        #something wrong, show the error
        err = out.get('error', out.get('reason', 'Invalid query!'))
        print('<p>Error:<pre>&nbsp;%s</pre></p>' % err)

else:
   geneid = params.get('showgene',[''])[0]
   if geneid:
        #show gene page
        gene = call_service('/v2/gene/%s?fields=reporter' % geneid)
        ps_list = []
        if gene and 'reporter' in gene:
            ps_list = gene['reporter'].get('Mouse430_2',[])
            if PY3:
                if type(ps_list) is not list:
                    ps_list = [ps_list]
            else:
                if type(ps_list) is not types.ListType:
                    # if only one probeset available, it's returned as a string, so we need to convert it to a list
                    ps_list = [ps_list]
        if ps_list:
            for ps in ps_list:
                print('<img src="http://biogps.org/dataset/4/chart/%s">' % ps)
        else:
            print('<p>No data available for this gene.</p>')


print('</html>')



