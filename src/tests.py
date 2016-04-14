# -*- coding: utf-8 -*-
# Copyright [2010-2014] [Chunlei Wu]
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
import sys
import os
import json
import httplib2
from nose.tools import ok_, eq_
if sys.version > '3':
    PY3 = True
else:
    PY3 = False
if PY3:
    import urllib.request
    import urllib.parse
    import urllib.error
else:
    import urllib

try:
    import msgpack
except ImportError:
    sys.stderr.write("Warning: msgpack is not available.")

host = os.getenv("MG_HOST")
if not host:
    #host = 'http://localhost:8000'
    #host = 'http://dev.mygene.info:8000'
    host = 'http://mygene.info'
api = host + '/v2'
sys.stderr.write('URL base: {}\n'.format(api))

h = httplib2.Http()
_d = json.loads    # shorthand for json decode
_e = json.dumps    # shorthand for json encode


#############################################################
# Hepler functions                                          #
#############################################################
def encode_dict(d):
    '''urllib.urlencode (python 2.x) cannot take unicode string.
       encode as utf-8 first to get it around.
    '''
    if PY3:
        return dict([(key, val.encode('utf-8')) for key, val in d.items()
                     if isinstance(val, str)])
    else:
        return dict([(key, val.encode('utf-8')) for key, val in d.iteritems()
                     if isinstance(val, basestring)])


def truncate(s, limit):
    '''truncate a string.'''
    if len(s) <= limit:
        return s
    else:
        return s[:limit] + '...'


def json_ok(s, checkerror=True):
    d = _d(s.decode('utf-8'))
    if checkerror:
        ok_(not (isinstance(d, dict) and 'error' in d), truncate(str(d), 1000000))
    return d


def msgpack_ok(b, checkerror=True):
    #print(b)
    d = msgpack.unpackb(b)
    if checkerror:
        ok_(not (isinstance(d, dict) and 'error' in d), truncate(str(d), 100))
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
    if PY3:
        res, con = h.request(url, 'POST', urllib.parse.urlencode(encode_dict(params)), headers=headers)
    else:
        res, con = h.request(url, 'POST', urllib.urlencode(encode_dict(params)), headers=headers)
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
    print('Testing "%s"...' % host)


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
               'taxid', 'type_of_gene', 'unigene', 'uniprot', 'exons', 'generif']
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
    assert 'snowball' in res.get('reporter', {}), 'Missing field "reporter.snowball" in gene "397593"'

    #nematode
    res = json_ok(get_ok(api + '/gene/172677'))
    res = json_ok(get_ok(api + '/gene/9821293'))    # this is not nematode, "taxid": 31234
    attr = 'WormBase'
    assert res.get(attr, None) is not None, 'Missing field "{}" in gene "9821293"'.format(attr)

    #fission yeast
    res = json_ok(get_ok(api + '/gene/2539869'))

    #e coli.
    #res = json_ok(get_ok(api + '/gene/12931566'))

    #mirna
    res = json_ok(get_ok(api + '/gene/406881'))
    attr = 'miRBase'
    assert res.get(attr, None) is not None, 'Missing field "{}" in gene "406881"'.format(attr)


def has_hits(q):
    d = json_ok(get_ok(api + '/query?q='+q))
    ok_(d.get('total', 0) > 0 and len(d.get('hits', [])) > 0)


def test_query():
    #public query api at /query via get
    # json_ok(get_ok(api + '/query?q=cdk2'))
    # json_ok(get_ok(api + '/query?q=GO:0004693'))
    # json_ok(get_ok(api + '/query?q=211803_at'))
    has_hits('cdk2')
    has_hits('GO:0004693')
    has_hits('211803_at')
    has_hits('IPR008351')
    has_hits('hsa-mir-503')
    has_hits('hsa-miR-503')

    #test fielded query
    has_hits('symbol:cdk2')
    #test interval query
    has_hits('chr1:151,073,054-151,383,976&species=human')

    con = get_ok(api + '/query?q=cdk2&callback=mycallback')
    ok_(con.startswith(b'mycallback('))

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
    assert len(res) >= 4, (res, len(res))
    res = json_ok(post_ok(api + '/query', {}), checkerror=False)
    assert 'error' in res, res

    res = json_ok(post_ok(api + '/query', {'q': '[1017, "1018"]',
                                           'scopes': 'entrezgene',
                                           'jsoninput': 'true'}))
    eq_(len(res), 2)
    eq_(res[0]['_id'], '1017')
    eq_(res[1]['_id'], '1018')


def test_query_interval():
    res = json_ok(get_ok(api + '/query?q=chr1:1000-100000&species=human'))
    ok_(len(res['hits']) > 1)
    ok_('_id' in res['hits'][0])


def test_query_size():
    res = json_ok(get_ok(api + '/query?q=cdk?'))
    eq_(len(res['hits']), 10)  # default is 10
    ok_(res['total'] > 10)

    res = json_ok(get_ok(api + '/query?q=cdk?&size=0'))
    eq_(len(res['hits']), 0)

    res = json_ok(get_ok(api + '/query?q=cdk?&limit=20'))
    eq_(len(res['hits']), 20)

    res1 = json_ok(get_ok(api + '/query?q=cdk?&from=0&size=20'))
    #res2 = json_ok(get_ok(api + '/query?q=cdk*&from=0&size=20'))
    res = json_ok(get_ok(api + '/query?q=cdk?&skip=10&size=20'))
    #eq_([x['_id'] for x in res1['hits']],[x['_id'] for x in res2['hits']])
    eq_(len(res['hits']), 20)
    #print res1['hits'].index(res['hits'][0])
    #print [x['_id'] for x in res1['hits']]
    #eq_(res['hits'][0], res1['hits'][10])
    assert res['hits'][0] in res1['hits']

    # API doc says cap 1000
    res = json_ok(get_ok(api + '/query?q=*&size=1000'))
    eq_(len(res['hits']), 1000)
    res = json_ok(get_ok(api + '/query?q=*&size=1001'))
    eq_(len(res['hits']), 1000)
    res = json_ok(get_ok(api + '/query?q=*&size=2000'))
    eq_(len(res['hits']), 1000)

    #assert 1==0
    res = json_ok(get_ok(api + '/query?q=cdk?&size=1a'), checkerror=False)  # invalid size parameter
    assert 'error' in res


def test_gene():
    res = json_ok(get_ok(api + '/gene/1017'))
    eq_(res['entrezgene'], 1017)
    # testing non-ascii character
    get_404(api + '/gene/' + '54097\xef\xbf\xbd\xef\xbf\xbdmouse')

    # commented out this test, as no more
    #allow dot in the geneid
    #res = json_ok(get_ok(api + '/gene/Y105C5B.255'))

    # testing filtering parameters
    res = json_ok(get_ok(api + '/gene/1017?fields=symbol,name,entrezgene'))
    eq_(set(res), set(['_id', '_version', 'symbol', 'name', 'entrezgene']))
    res = json_ok(get_ok(api + '/gene/1017?filter=symbol,go.MF'))
    eq_(set(res), set(['_id', '_version', 'symbol', 'go']))
    assert "MF" in res["go"]
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
        eq_(set(_g), set(['_id', '_score', 'query', 'symbol', 'name', 'entrezgene']))

    res = json_ok(post_ok(api + '/gene', {'ids': '1017,1018', 'filter': 'symbol,go.MF'}))
    eq_(len(res), 2)
    for _g in res:
        eq_(set(_g), set(['_id', '_score', 'query', 'symbol', 'go']))
        assert "MF" in _g["go"]


def test_status():
    #/status
    get_ok(host + '/status')
    head_ok(host + '/status')


def test_metadata():
    root = json_ok(get_ok(host + '/metadata'))
    v2 = json_ok(get_ok(api + '/metadata'))
    eq_(root,v2)
    eq_(set(root.keys()),set(['available_fields', 'src_version', 'app_revision', 'timestamp', 'taxonomy',
        'stats','genome_assembly','source']))
    fields =json_ok(get_ok(api + '/metadata/fields'))
    # test random field
    assert "refseq" in fields
    assert "accession.rna" in fields
    assert "interpro.desc" in fields
    assert "homologene" in fields
    assert "reporter.snowball" in fields


def test_query_facets():
    res = json_ok(get_ok(api + '/query?q=cdk?&facets=taxid'))
    ok_('facets' in res)
    ok_('taxid' in res['facets'])
    eq_(res['facets']['taxid']['total'], res['total'])
    eq_(res['facets']['taxid']['other'], 0)
    eq_(res['facets']['taxid']['missing'], 0)

    res2 = json_ok(get_ok(api + '/query?q=cdk?&facets=taxid&species_facet_filter=human'))
    eq_(res2['facets']['taxid']['total'], res['total'])
    eq_(res2['facets']['taxid'], res['facets']['taxid'])
    eq_([x["count"] for x in res2['facets']['taxid']['terms'] if x["term"] == 9606][0], res2['total'])


def test_query_userfilter():
    res1 = json_ok(get_ok(api + '/query?q=cdk'))
    res2 = json_ok(get_ok(api + '/query?q=cdk&userfilter=bgood_cure_griffith'))
    ok_(res1['total'] > res2['total'])

    res2 = json_ok(get_ok(api + '/query?q=cdk&userfilter=aaaa'))   # nonexisting user filter gets ignored.
    eq_(res1['total'], res2['total'])


def test_existsfilter():
    res1 = json_ok(get_ok(api + '/query?q=cdk'))
    res2 = json_ok(get_ok(api + '/query?q=cdk&exists=pharmgkb'))
    ok_(res1['total'] > res2['total'])
    res3 = json_ok(get_ok(api + '/query?q=cdk&exists=pharmgkb,pdb'))
    ok_(res2['total'] > res3['total'])


def test_missingfilter():
    res1 = json_ok(get_ok(api + '/query?q=cdk'))
    res2 = json_ok(get_ok(api + '/query?q=cdk&missing=pdb'))
    ok_(res1['total'] > res2['total'])
    res3 = json_ok(get_ok(api + '/query?q=cdk&missing=pdb,MIM'))
    ok_(res2['total'] > res3['total'])


def test_unicode():
    s = u'基因'

    get_404(api + '/gene/' + s)

    res = json_ok(post_ok(api + '/gene', {'ids': s}))
    eq_(res[0]['notfound'], True)
    eq_(len(res), 1)
    res = json_ok(post_ok(api + '/gene', {'ids': '1017, ' + s}))
    eq_(res[1]['notfound'], True)
    eq_(len(res), 2)

    res = json_ok(get_ok(api + '/query?q=' + s))
    eq_(res['hits'], [])

    res = json_ok(post_ok(api + '/query', {"q": s, "scopes": 'symbol'}))
    eq_(res[0]['notfound'], True)
    eq_(len(res), 1)

    res = json_ok(post_ok(api + '/query', {"q": 'cdk2+' + s}))
    eq_(res[1]['notfound'], True)
    eq_(len(res), 2)


def test_hg19():
    res = json_ok(get_ok(api + '/query?q=hg19.chr12:57,795,963-57,815,592&species=human'))
    ok_(len(res['hits']) == 2)
    ok_('_id' in res['hits'][0])
    res2 = json_ok(get_ok(api + '/query?q=chr12:57,795,963-57,815,592&species=human'))
    ok_(res['total'] != res2['total'])

    res = json_ok(get_ok(api + '/gene/10017?fields=genomic_pos_hg19,exons_hg19'))
    ok_('genomic_pos_hg19' in res)
    ok_('exons_hg19' in res)


def test_mm9():
    res = json_ok(get_ok(api + '/query?q=mm9.chr12:57,795,963-57,815,592&species=mouse'))
    ok_(len(res['hits']) == 2)
    ok_('_id' in res['hits'][0])
    res2 = json_ok(get_ok(api + '/query?q=chr12:57,795,963-57,815,592&species=mouse'))
    ok_(res['total'] != res2['total'])

    res = json_ok(get_ok(api + '/gene/12049?fields=genomic_pos_mm9,exons_mm9'))
    ok_('genomic_pos_mm9' in res)
    ok_('exons_mm9' in res)


def test_msgpack():
    res = json_ok(get_ok(api + '/gene/1017'))
    res2 = msgpack_ok(get_ok(api + '/gene/1017?msgpack=true'))
    ok_(res, res2)

    res = json_ok(get_ok(api + '/query/?q=cdk'))
    res2 = msgpack_ok(get_ok(api + '/query/?q=cdk&msgpack=true'))
    ok_(res, res2)

    res = json_ok(get_ok(api + '/metadata'))
    res2 = msgpack_ok(get_ok(api + '/metadata?msgpack=true'))
    ok_(res, res2)


def test_taxonomy():
    res = json_ok(get_ok(api + '/species/1239'))
    ok_("lineage" in res)

    res = json_ok(get_ok(api + '/species/46170?include_children=true'))
    ok_(len(res['children']) >= 305)

    res2 = json_ok(get_ok(api + '/species/46170?include_children=true&has_gene=1'))
    ok_(len(res2['children']) >= 16)
    ok_(len(res2['children']) <= len(res['children']))

    res = json_ok(get_ok(api + '/query?q=lytic%20enzyme&species=1386&include_tax_tree=true'))
    ok_(res['total'] >= 2)
    res2 = json_ok(get_ok(api + '/query?q=lytic%20enzyme&species=1386'))
    eq_(res2['total'], 0)


def test_static():
    get_ok(host + '/favicon.ico')
    get_ok(host + '/robots.txt')


def test_fetch_all():
    res = json_ok(get_ok(api + '/query?q=cdk2&fetch_all=true'))
    assert '_scroll_id' in res

    res2 = json_ok(get_ok(api + '/query?scroll_id=' + res['_scroll_id']))
    assert 'hits' in res2
    ok_(len(res2['hits']) >= 2)

def test_dotfield():
    # /query service
    resdefault = json_ok(get_ok(api + '/query?q=cdk&fields=refseq.rna')) # default dotfield=0
    resfalse = json_ok(get_ok(api + '/query?q=cdk&fields=refseq.rna&dotfield=false')) # force no dotfield
    restrue = json_ok(get_ok(api + '/query?q=cdk&fields=refseq.rna&dotfield=true')) # force dotfield
    # check defaults and bool params
    eq_(resdefault["hits"],resfalse["hits"])
    # check struct
    assert "refseq.rna" in restrue["hits"][0].keys()
    assert "refseq" in resdefault["hits"][0].keys()
    assert "rna" in resdefault["hits"][0]["refseq"].keys()
    # TODO: no fields but dotfield => dotfield results
    # TODO: fields with dot but no dotfield => dotfield results

    # /gene service
    resdefault = json_ok(get_ok(api + '/gene/1017?filter=symbol,go.MF'))
    restrue = json_ok(get_ok(api + '/gene/1017?filter=symbol,go.MF&dotfield=true'))
    resfalse = json_ok(get_ok(api + '/gene/1017?filter=symbol,go.MF&dotfield=false'))
    eq_(resdefault,resfalse)
    assert "go.MF" in restrue.keys()
    assert "go" in resdefault.keys()
    assert "MF" in resdefault["go"].keys()
    
def test_raw():
    # /gene
    raw1 = json_ok(get_ok(api + '/gene/1017?raw=1'))
    rawtrue = json_ok(get_ok(api + '/gene/1017?raw=true'))
    raw0  = json_ok(get_ok(api + '/gene/1017?raw=0'))
    rawfalse  = json_ok(get_ok(api + '/gene/1017?raw=false'))
    eq_(raw1,rawtrue)
    eq_(raw0,rawfalse)
    assert "_index" in raw1
    assert not "_index" in raw0
    assert "_source" in raw1
    assert not "_source" in raw0
    # /query
    raw1 = json_ok(get_ok(api + '/query?q=cdk&raw=1'))
    rawtrue = json_ok(get_ok(api + '/query?q=cdk&raw=true'))
    raw0  = json_ok(get_ok(api + '/query?q=cdk&raw=0'))
    rawfalse  = json_ok(get_ok(api + '/query?q=cdk&raw=false'))
    # this may vary so remove in comparison
    for d in [raw1,rawtrue,raw0,rawfalse]:
        del d["took"]
    eq_(raw1,rawtrue)
    eq_(raw0,rawfalse)
    assert "_shards" in raw1
    assert not "_shards" in raw0

def test_species():
    res, con = h.request(api + "/species/9606")
    eq_(res.status, 200)
    eq_(res["content-location"],'http://s.biothings.io/v1/species/9606?include_children=1')
    d = _d(con.decode('utf-8'))
    eq_(set(d.keys()),set(['taxid', 'authority', 'lineage', '_id', 'common_name', 'genbank_common_name', '_version',
        'parent_taxid', 'scientific_name', 'has_gene', 'children', 'rank', 'uniprot_name']))
    

