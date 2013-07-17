# Copyright [2010-2011] [Chunlei Wu]
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


'''
Nose tests
run as "nosetests tests"
    or "nosetests tests:test_main"
'''
import types
import httplib2
import urllib
import json
from nose.tools import ok_, eq_, with_setup

host='http://localhost:9000'
api = host + '/v2'

h = httplib2.Http()
_d = json.loads    # shorthand for json decode
_e = json.dumps    # shorthand for json encode

#############################################################
# Hepler functions                                          #
#############################################################
def truncate(s, limit):
    '''truncate a string.'''
    if len(s) <= limit:
        return s
    else:
        return s[:limit] + '...'

def json_ok(s, checkerror=True):
    d = _d(s)
    if checkerror:
        ok_(not (type(d) is types.DictType and 'error' in d), truncate(str(d), 100))
    return d

def get_ok(url):
    res, con = h.request(url)
    eq_(res.status, 200)
    return con

def get_404(url):
    res, con = h.request(url)
    eq_(res.status, 404)

def get_405(url):
    res, con = h.request(url)
    eq_(res.status, 405)

def head_ok(url):
    res, con = h.request(url, 'HEAD')
    eq_(res.status, 200)

def post_ok(url, params):
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    res, con = h.request(url, 'POST', urllib.urlencode(params), headers=headers)
    eq_(res.status, 200)
    return con

def w_cdk2(res):
    '''test "res" object for:
           1. contains more than one gene
           2. gene cdk2 (1017) is included
    '''
    ok_(len(res) > 1)
    ok_('1017' in set([x['id'] for x in res]))


def setup_func():
    print 'Testing "%s"...' % host

def teardown_func():
    pass

#############################################################
# Test functions                                            #
#############################################################
#@with_setup(setup_func, teardown_func)
def test_main():
    #/
    get_ok(host)


def test_gene_object():
    #test all fields are load in gene objects
    res = json_ok(get_ok(api + '/gene/1017'))

    attr_li = ['HGNC', 'HPRD', 'MIM', 'Vega', '_id', 'accession', 'alias',
               'ec', 'ensembl', 'entrezgene', 'genomic_pos', 'go', 'homologene',
               'interpro', 'ipi', 'map_location', 'name', 'pdb', 'pharmgkb', 'pir',
               'prosite', 'reagent', 'refseq', 'reporter', 'summary', 'symbol',
               'taxid', 'type_of_gene', 'unigene', 'uniprot']
    for attr in attr_li:
        assert res.get(attr, None) is not None, 'Missing field "{}" in gene "1017"'.format(attr)

    res = json_ok(get_ok(api + '/gene/12566'))
    attr = 'MGI'
    assert res.get(attr, None) is not None, 'Missing field "{}" in gene "12566"'.format(attr)

    res = json_ok(get_ok(api + '/gene/245962'))
    attr = 'RGD'
    assert res.get(attr, None) is not None, 'Missing field "{}" in gene "245962"'.format(attr)

    res = json_ok(get_ok(api + '/gene/493498'))
    attr = 'Xenbase'
    assert res.get(attr, None) is not None, 'Missing field "{}" in gene "493498"'.format(attr)

    res = json_ok(get_ok(api + '/gene/406715'))
    attr = 'ZFIN'
    assert res.get(attr, None) is not None, 'Missing field "{}" in gene "406715"'.format(attr)

    res = json_ok(get_ok(api + '/gene/824036'))
    attr = 'TAIR'
    assert res.get(attr, None) is not None, 'Missing field "{}" in gene "824036"'.format(attr)

    res = json_ok(get_ok(api + '/gene/42453'))
    attr = 'FLYBASE'
    assert res.get(attr, None) is not None, 'Missing field "{}" in gene "42453"'.format(attr)

    #pig
    res = json_ok(get_ok(api + '/gene/397593'))
    assert res.get('reporter', {}).has_key('snowball'), 'Missing field "reporter.snowball" in gene "397593"'

    #nematode
    res = json_ok(get_ok(api + '/gene/172677'))
    res = json_ok(get_ok(api + '/gene/9821293'))    #this is not nematode, "taxid": 31234
    attr = 'WormBase'
    assert res.get(attr, None) is not None, 'Missing field "{}" in gene "9821293"'.format(attr)

    #fission yeast
    res = json_ok(get_ok(api + '/gene/2539869'))

    #e coli.
    res = json_ok(get_ok(api + '/gene/12931566'))

    #mirna
    res = json_ok(get_ok(api + '/gene/406881'))
    attr = 'miRBase'
    assert res.get(attr, None) is not None, 'Missing field "{}" in gene "406881"'.format(attr)


def test_query():
    #public query api at /query via get
    json_ok(get_ok(api + '/query?q=cdk2'))
    json_ok(get_ok(api + '/query?q=GO:0004693'))
    json_ok(get_ok(api + '/query?q=211803_at'))

    #test fielded query
    json_ok(get_ok(api + '/query?q=symbol:cdk2'))
    #test interval query
    json_ok(get_ok(api + '/query?q=chr1:151,073,054-151,383,976&species=human'))

    con = get_ok(api + '/query?q=cdk2&callback=mycallback')
    ok_(con.startswith('mycallback('))

    # testing non-ascii character
    res = json_ok(get_ok(api + '/query?q=54097\xef\xbf\xbd\xef\xbf\xbdmouse'))
    eq_(res['hits'], [])

    res = json_ok(get_ok(api + '/query'), checkerror=False)
    assert 'error' in res

    res = json_ok(get_ok(api + '/query?q=tRNA:Y1:85Ae'), checkerror=False)
    assert 'error' in res

def test_query_post():
    #/query via post
    json_ok(post_ok(api + '/query', {'q': '1017'}))

    res = json_ok(post_ok(api + '/query', {'q': '1017',
                                            'scopes': 'entrezgene'}))
    eq_(len(res), 1)
    eq_(res[0]['_id'], '1017')

    res = json_ok(post_ok(api + '/query', {'q': '211803_at,1018',
                                            'scopes': 'reporter,entrezgene'}))
    eq_(len(res), 2)
    eq_(res[0]['_id'], '1017')
    eq_(res[1]['_id'], '1018')

    res = json_ok(post_ok(api + '/query', {'q': 'CDK2',
                                            'species': 'human,10090,frog,pig',
                                            'scopes': 'symbol',
                                            'fields': 'name,symbol'}))
    assert len(res) == 4, (res, len(res))
    res = json_ok(post_ok(api + '/query', {}), checkerror=False)
    assert 'error' in res, res

def test_query_interval():
    res = json_ok(get_ok(api + '/query?q=chr1:1000-100000&species=human'))
    ok_(len(res['hits'])>1)
    ok_('_id' in res['hits'][0])


def test_gene():
    res = json_ok(get_ok(api + '/gene/1017'))
    eq_(res['entrezgene'], 1017)

    # testing non-ascii character
    get_404(api + '/gene/' + '54097\xef\xbf\xbd\xef\xbf\xbdmouse')

    #allow dot in the geneid
    res = json_ok(get_ok(api + '/gene/Y105C5B.255'))

    # testing filtering parameters
    res = json_ok(get_ok(api + '/gene/1017?fields=symbol,name,entrezgene'))
    eq_(set(res), set(['_id', 'symbol', 'name', 'entrezgene']))
    res = json_ok(get_ok(api + '/gene/1017?filter=symbol,go.MF'))
    eq_(set(res), set(['_id', 'symbol', 'go.MF']))
    #eq_(res['go'].keys(), ['MF'])

    get_404(api + '/gene')
    get_404(api + '/gene/')

    #res = json_ok(get_ok(api + '/boc/bgps/gene/1017'))
    #ok_('SpeciesList' in res)

def test_gene_post():
    res = json_ok(post_ok(api + '/gene', {'ids': '1017'}))
    eq_(len(res), 1)
    eq_(res[0]['entrezgene'], 1017)

    res = json_ok(post_ok(api + '/gene', {'ids': '1017, 1018'}))
    eq_(len(res), 2)
    eq_(res[0]['_id'], '1017')
    eq_(res[1]['_id'], '1018')

    res = json_ok(post_ok(api + '/gene', {'ids': '1017,1018', 'fields': 'symbol,name,entrezgene'}))
    eq_(len(res), 2)
    for _g in res:
        eq_(set(_g), set(['_id', 'query', 'symbol', 'name', 'entrezgene']))

    res = json_ok(post_ok(api + '/gene', {'ids': '1017,1018', 'filter': 'symbol,go.MF'}))
    eq_(len(res), 2)
    for _g in res:
        eq_(set(_g), set(['_id', 'query', 'symbol', 'go.MF']))


def test_status():
    #/status
    get_ok(host + '/status')
    head_ok(host + '/status')


def test_metadata():
    get_ok(host + '/metadata')
    get_ok(api + '/metadata')


