'''
    MyGene Remote Server Tester
    > python remote.py
'''

import os
import random

from nose import SkipTest
from nose.core import runmodule
from nose.tools import eq_, ok_

from biothings.tests import BiothingsTestCase
from biothings.tests.helper import equal


class MyGeneRemoteTest(BiothingsTestCase):
    ''' Test against server specified in environment variable BT_HOST
        or MyGene.info production server if BT_HOST is not specified
        BT_HOST must start with its protocol like http://mygene.info '''

    __test__ = True

    host = os.getenv("BT_HOST", "http://mygene.info").rstrip('/')
    api = '/v3'

    # Helper Function

    @staticmethod
    def filter_hits(dic, field=None):
        ''' Filter hits by removing specified fields or by default meta fields '''
        res = dict(dic)
        for hit in res.get("hits"):
            if field:
                del hit[field]
            else:
                # because can't remove elem from dict while iterate
                # need to keep track on what should be popped...
                topop = []
                for k in hit.keys():
                    if k.startswith("_"):
                        topop.append(k)
                for i in topop:
                    hit.pop(i)
        return res

    # Test Cases

    def test_000(self):
        ''' NETWORK Connection '''
        self.request(self.host)

    def test_101_gene(self):
        ''' ANNOTATION GET Field Completeness '''

        res = self.request('gene/1017').json()

        attr_li = ['HGNC', 'MIM', '_id', 'accession', 'alias',
                   'ec', 'ensembl', 'entrezgene', 'genomic_pos', 'go',
                   'homologene', 'interpro', 'ipi', 'map_location', 'name',
                   'pdb', 'pharmgkb', 'pir', 'prosite', 'reagent', 'refseq',
                   'reporter', 'summary', 'symbol', 'taxid', 'type_of_gene',
                   'unigene', 'uniprot', 'exons', 'generif']
        # Removed 'Vega' as an attribute in tests 2019/3

        for attr in attr_li:
            assert attr in res, 'Missing field "{}" in gene "1017"'.format(attr)

        pairs = [
            (12566, 'MGI'),
            (245962, 'RGD'),
            (493498, 'Xenbase'),
            (406715, 'ZFIN'),
            (824036, 'TAIR'),
            (42453, 'FLYBASE')
        ]

        for _id, attr in pairs:
            res = self.request('gene/' + str(_id)).json()
            assert attr in res, f'Missing field "{attr}" in gene "{_id}"'

        # pig
        res = self.request('gene/397593').json()
        assert 'reporter' in res, 'Missing field "reporter.snowball" in gene "397593"'
        assert 'snowball' in res['reporter'], 'Missing field "reporter.snowball" in gene "397593"'

        # nematode
        res = self.request('gene/172677').json()
        # this is not nematode, "taxid": 31234
        res = self.request('gene/9821293').json()
        attr = 'WormBase'
        assert attr in res, 'Missing field "{}" in gene "9821293"'.format(attr)

        # fission yeast
        res = self.request('gene/2539869').json()

        # e coli.
        # res = self.request('gene/12931566').json()

        # mirna
        res = self.request('gene/406881').json()
        attr = 'miRBase'
        assert attr in res, 'Missing field "{}" in gene "406881"'.format(attr)

    def test_102_gene(self):
        ''' ANNOTATION GET Bad Request Handling '''

        res = self.request('gene/1017').json()
        eq_(res['entrezgene'], "1017")

        # testing non-ascii character
        self.request('gene/54097\xef\xbf\xbd\xef\xbf\xbdmouse',
                     expect_status=404)

        # one test to /gene/Y105C5B.255 has been removed
        # since dots in geneids are no longer supported

        self.request('gene', expect_status=404)
        self.request('gene/', expect_status=404)

    def test_103_gene(self):
        ''' ANNOTATION POST '''

        res = self.request('gene', method='POST', data={'ids': '1017'}).json()
        eq_(len(res), 1)
        # check default fields returned
        default_fields = [
            'symbol', 'reporter', 'refseq', '_score', 'pdb', 'interpro', 'entrezgene', 'summary',
            'genomic_pos_hg19', 'unigene', 'ipi', 'taxid', 'pfam', 'homologene', 'ensembl', 'ec',
            'pir', 'type_of_gene', 'pathway', 'exons_hg19', 'MIM', 'generif', 'HGNC', 'name',
            'reagent', 'uniprot', 'pharmgkb', 'alias', 'genomic_pos', 'accession', '_id', 'prosite',
            'wikipedia', 'go', 'query', 'map_location', 'exons', 'exac', 'other_names', 'umls',
            'pantherdb', 'pharos']
        equal('Retrived fields', set(res[0].keys()), 'Reference fields', set(default_fields))
        eq_(res[0]['entrezgene'], "1017")

        res = self.request('gene', method='POST', data={'ids': '1017, 1018'}).json()
        eq_(len(res), 2)
        eq_(res[0]['_id'], '1017')
        eq_(res[1]['_id'], '1018')

        data = {'ids': '1017,1018',
                'fields': 'symbol,name,entrezgene'}
        res = self.request('gene', method='POST', data=data).json()
        eq_(len(res), 2)
        for _g in res:
            eq_(set(_g), set(['_id', '_score', 'query', 'symbol',
                              'name', 'entrezgene']))

        data = {'ids': '1017,1018',
                'filter': 'symbol,go.MF'}
        res = self.request('gene', method='POST', data=data).json()
        eq_(len(res), 2)
        for _g in res:
            eq_(set(_g), set(['_id', '_score', 'query', 'symbol', 'go']))
            assert "MF" in _g["go"]

        # get retired gene
        res = self.request('gene', method='POST', data={'ids': '791256'}).json()
        eq_(res[0]['_id'], '50846')  # this is the corresponding _id field

    def test_201_query(self):
        ''' QUERY GET '''

        # data existance
        self.query(q='cdk2')
        self.query(q='GO:0004693')
        self.query(q='reporter:211803_at')
        self.query(q='IPR008351')
        self.query(q='hsa-mir-503')
        self.query(q='hsa-miR-503')

        # fielded query
        self.query(q='symbol:cdk2')

        # interval query
        self.query(q='chr1:151,073,054-151,383,976&species=human')

        con = self.request('query?q=cdk2&callback=mycallback').content
        assert con.startswith(b'mycallback(')

        # non-ascii character
        res = self.query(q='54097\xef\xbf\xbd\xef\xbf\xbdmouse', expect_hits=False)
        eq_(res['hits'], [])

        self.request('query', expect_status=400)

        self.request('query?q=tRNA:Y1:85Ae', expect_status=400)

        # default returned fields
        res = self.request('query?q=cdk').json()
        idx = random.randrange(0, 10)  # pick one
        deffields = res["hits"][idx].keys()  # pick one...
        expected = ["_id", "_score", "taxid", "entrezgene", "name", "symbol"]
        assert sorted(list(deffields)) == sorted(expected), \
            "%s != %s" % (sorted(list(deffields)), sorted(expected))

    def test_202_query(self):
        ''' QUERY GET ES_KWarg Size '''
        res = self.request('query?q=cdk?').json()
        eq_(len(res['hits']), 10)  # default is 10
        ok_(res['total'] > 10)

        res = self.request('query?q=cdk?&size=0').json()
        eq_(len(res['hits']), 0)

        res = self.request('query?q=cdk?&limit=20').json()
        eq_(len(res['hits']), 20)

        res1 = self.request("query?q=cdk?&from=0&size=20").json()
        res = self.request("query?q=cdk?&skip=10&size=20").json()
        eq_(len(res['hits']), 20)
        assert res['hits'][0] in res1['hits']

        # API doc says cap 1000
        res = self.request('query?q=*&size=1000').json()
        eq_(len(res['hits']), 1000)
        res = self.request('query?q=*&size=1001').json()
        eq_(len(res['hits']), 1000)
        res = self.request('query?q=*&size=2000').json()
        eq_(len(res['hits']), 1000)

        self.request('query?q=cdk?&size=1a', expect_status=400)

    def test_203_query(self):
        ''' QUERY GET ES_KWarg Aggregation/Facets '''
        res = self.request('query?q=cdk?&facets=taxid&species=human,mouse,rat').json()
        ok_('facets' in res)
        ok_('taxid' in res['facets'])
        eq_(res['facets']['taxid']['total'], res['total'])
        eq_(res['facets']['taxid']['other'], 0)
        eq_(res['facets']['taxid']['missing'], 0)

        res_t = self.request(
            "query?q=symbol:cdk?&facets=type_of_gene&species=human,mouse,rat").json()
        ok_('facets' in res_t)
        ok_('type_of_gene' in res_t['facets'])
        assert "term" in res_t['facets']['type_of_gene']['terms'][0]
        eq_(res_t['facets']['type_of_gene']
            ['terms'][0]['term'], 'protein-coding')

        url = 'query?q=cdk?&facets=taxid&species_facet_filter=human&species=human,mouse,rat'
        res2 = self.request(url).json()
        eq_(res2['facets']['taxid']['total'], res['total'])
        eq_(res2['facets']['taxid'], res['facets']['taxid'])
        eq_([x["count"] for x in res2['facets']['taxid']['terms']
             if x["term"] == 9606][0], res2['total'])

    def test_204_query(self):
        ''' QUERY GET ES_KWarg Sort '''
        res = self.request("query?q=MTFMT&sort=taxid&species=human,mouse,rat").json()
        hits = res["hits"]
        assert len(hits) == 3
        eq_(hits[0]["entrezgene"], "123263")
        eq_(hits[1]["entrezgene"], "69606")
        eq_(hits[2]["entrezgene"], "315763")

    def test_205_query(self):
        ''' QUERY GET ESQB_KWarg Userquery '''

        res1 = self.request('query?q=cdk').json()
        res2 = self.request("query?q=cdk&userquery=bgood_cure_griffith").json()
        ok_(res1['total'] > res2['total'])

        # nonexisting user filter gets ignored
        res2 = self.request("query?q=cdk&userquery=aaaa").json()
        eq_(res1['total'], res2['total'])

    def test_206_query(self):
        ''' QUERY GET ESQB_KWarg Exists '''
        res1 = self.request('query?q=cdk').json()
        res2 = self.request("query?q=cdk&exists=pharmgkb").json()
        ok_(res1['total'] > res2['total'])
        res3 = self.request("query?q=cdk&exists=pharmgkb,pdb").json()
        ok_(res2['total'] > res3['total'])

    def test_207_query(self):
        ''' QUERY GET ESQB_KWarg Missing '''
        res1 = self.request('query?q=cdk').json()
        res2 = self.request('query?q=cdk&missing=pdb').json()
        ok_(res1['total'] > res2['total'])
        res3 = self.request("query?q=cdk&missing=pdb,MIM").json()
        ok_(res2['total'] > res3['total'])

    def test_208_query(self):
        ''' QUERY GET ESQB_KWarg Genomic Interval '''
        self.query(q='chr1:1000-100000', species='human')

    def test_209_query(self):
        ''' QUERY GET ESQB_KWarg Fetch_all '''

        # this keyword argument is also a control keyword

        res = self.request("query?q=cdk*&species=all&fetch_all=true").json()
        assert '_scroll_id' in res

        res2 = self.query(scroll_id=res['_scroll_id'])
        assert 'hits' in res2
        ok_(len(res2['hits']) >= 2)

    def test_210_query(self):
        ''' QUERY GET ESQB_KWarg Include_tax_tree '''

        url = 'query?q=lytic%20enzyme&species=1386&include_tax_tree=true'
        res = self.request(url).json()
        ok_(res['total'] >= 2)
        res2 = self.request("query?q=lytic%20enzyme&species=1386").json()
        eq_(res2['total'], 0)

    def test_211_query(self):
        ''' QUERY POST '''

        data = {'q': '1017', 'scopes': 'entrezgene'}
        res = self.request('query', method='POST', data=data).json()
        eq_(len(res), 1)
        eq_(set(res[0].keys()), set(
            ['query', 'taxid', '_score', 'entrezgene', 'symbol', '_id', 'name']))
        eq_(res[0]['_id'], '1017')

        data = {'q': '211803_at,1018', 'scopes': 'reporter,entrezgene'}
        res = self.request('query', method='POST', data=data).json()
        eq_(len(res), 2)
        eq_(res[0]['_id'], '1017')
        eq_(res[1]['_id'], '1018')

        data = {'q': 'CDK2',
                'species': 'human,10090,frog,pig',
                'scopes': 'symbol',
                'fields': 'name,symbol'}
        res = self.request('query', method='POST', data=data).json()
        assert len(res) >= 4, (res, len(res))
        self.request('query', expect_status=400)

        data = {'q': '[1017, "1018"]',
                'scopes': 'entrezgene',
                'jsoninput': 'true'}
        res = self.request('query', method='POST', data=data).json()
        eq_(len(res), 2)
        eq_(res[0]['_id'], '1017')
        eq_(res[1]['_id'], '1018')

    def test_212_query(self):
        ''' QUERY POST List Handling '''

        body = {'q': '"cyclin dependent kinase 2", "cyclin dependent kinase 3"',
                'fields': 'entrezgene,  name',
                'species': 'human',
                'scopes': 'name'
                }

        res = self.query(method='POST', **body)
        query_set = {item['query'] for item in res}
        # make sure queries are interpreted correctly and returned
        assert query_set == set(
            ["cyclin dependent kinase 2", "cyclin dependent kinase 3"])
        # make sure fields are interpreted correctly
        field_set = set()
        for item in res:
            if 'entrezgene' in item:
                field_set.add('entrezgene')
            if 'name' in item:
                field_set.add('name')
        assert field_set == set(['entrezgene', 'name'])

    def test_301_web(self):
        ''' WEB Status Endpoint '''
        self.request('/status')
        self.request('/status', method='HEAD')

    def test_302_web(self):
        ''' WEB Static Content Serving '''
        self.request('/favicon.ico')
        self.request('/robots.txt')

    def test_303_web(self):
        ''' WEB Metadata Endpoint '''
        root_res = self.request('/metadata').json()
        api_res = self.request('metadata').json()
        equal(f"res({self.host + '/metadata'})", root_res,
              f"res({self.host + self.api + '/metadata'})", api_res)
        available_fields = {'available_fields', 'build_version',
                            'app_revision', 'build_date', 'taxonomy',
                            'stats', 'genome_assembly', 'src', 'source', 'biothing_type'}
        equal('Retrieved Meta fields', set(root_res.keys()), 'Reference fields', available_fields)
        fields = self.request('metadata/fields').json()
        # test random field
        assert "refseq" in fields
        assert "accession.rna" in fields
        assert "interpro.desc" in fields
        assert "homologene" in fields
        assert "reporter.snowball" in fields
        # debug info
        debug = self.request('metadata?dev=1').json()
        assert "software" in debug.keys()
        nodebug = self.request('metadata?dev=0').json()
        assert not "software" in nodebug.keys()

    def test_304_web(self):
        ''' WEB Taxonomy Redirect '''

        res = self.request('species/1239').json()
        ok_("lineage" in res)

        res = self.request("species/46170?include_children=true").json()
        ok_(len(res['children']) >= 305)

        res2 = self.request("species/46170?include_children=true&has_gene=1").json()
        ok_(len(res2['children']) >= 16)
        ok_(len(res2['children']) <= len(res['children']))

    def test_305_web(self):
        ''' WEB Species Endpoint '''
        dic = self.request("species/9606").json()
        eq_(set(dic.keys()), set(['taxid', 'authority', 'lineage', '_id',
                                  'common_name', 'genbank_common_name',
                                  '_version', 'parent_taxid', 'scientific_name',
                                  'has_gene', 'children', 'rank',
                                  'uniprot_name']))

    def test_401_unicode(self):
        ''' HANDLE Unicode Strings '''

        unicode_text = u'基因'

        self.request('gene/' + unicode_text, expect_status=404)

        res = self.request("gene", method='POST', data={'ids': unicode_text}).json()
        eq_(res[0]['notfound'], True)
        eq_(len(res), 1)
        res = self.request("gene", method='POST', data={'ids': '1017, ' + unicode_text}).json()
        eq_(res[1]['notfound'], True)
        eq_(len(res), 2)

        res = self.query(q=unicode_text, expect_hits=False)
        eq_(res['hits'], [])

        res = self.query(method='POST', q=unicode_text, scopes='symbol', expect_hits=False)
        eq_(res[0]['notfound'], True)
        eq_(len(res), 1)

        res = self.query(method='POST', q='cdk2+' + unicode_text, expect_hits=False)
        eq_(res[1]['notfound'], True)
        eq_(len(res), 2)

    def test_402_case_sensitivity(self):
        ''' HANDLE Case Insensitivity '''
        # case-insensitive sources
        self.query(q='mirbase:MI0017267')
        self.query(q='wormbase:WBGene00057218', species=31234)
        self.query(q='xenbase:XB-GENE-1001990', species='frog')
        self.query(q='Xenbase:XB-GENE-1001990', species='frog')
        self.query(q=r'mgi:MGI\\:104772')
        # sometimes the orders of results are *slightly* different for cdk2 and CDK2
        # so limit to top 3 more stable results
        lower = self.filter_hits(self.request("query?q=cdk2&size=3").json())
        upper = self.filter_hits(self.request("query?q=CDK2&size=3").json())
        eq_(lower["hits"], upper["hits"])

    def test_403_species_order(self):
        ''' HANDLE Species Order '''
        res = self.request("query?q=cdk2&species=human,mouse,rat").json()
        hits = res["hits"]
        # first is 1017, it's human and cdk2 is a symbol
        eq_(hits[0]["_id"], "1017")
        # second is 12566, mouse
        eq_(hits[1]["_id"], "12566")
        # third is 362817, rat
        eq_(hits[2]["_id"], "362817")

    def test_404_value_type(self):
        ''' HANDLE Numeric Value Type '''
        def check_homologene(res):
            for item in res["homologene"]["genes"]:
                eq_(type(item[0]), int)
                eq_(type(item[1]), int)

        def check_exons(res):
            for ex in res["exons"]:
                for pos in ex["position"]:
                    eq_(type(pos[0]), int)
                    eq_(type(pos[1]), int)
        res = self.request("gene/1017?species=9606&fields=homologene,exons").json()
        check_homologene(res)
        check_exons(res)
        resall = self.request("gene/1017?fields=homologene,exons").json()
        check_homologene(resall)
        check_exons(resall)

    @SkipTest
    def test_405_disambiguate_ensembl_entrez_ids(self):
        ''' HANDLE ensembl vs entriez id '''
        # some random test reported by users
        res = self.request("query?q=ensembl.transcript:ENSMUST00000161459").json()
        eq_(len(res["hits"]), 1)
        eq_(res["hits"][0]["symbol"], "Setdb2")
        res = self.request("gene/ENSG00000011454").json()
        # is now a list...these should all be redone
        # eq_(type(res),dict)
        # eq_(res["entrezgene"],"23637")
        # mapping no longer valid
        # res = self.request("/gene/ENSG00000237613"))
        # eq_(type(res),dict)
        # eq_(res["entrezgene"],"645520")
        # test "orphan" EntrezID (associated EnsemblIDs were all resolved
        # into other EntrezIDs but we want to keep ambiguated
        # Ensembl data for those)
        # res = self.request("/gene/100287596"))
        ###ensids = [e["gene"] for e in res["ensembl"]]
        # eq_(set(endids),{"ENSG00000248472","ENSG00000223972"})

    def test_501_kwargs(self):
        ''' KWARGS CTRL Format Msgpack '''

        # format and out_format are an aliases
        # effective for both annotation and query
        # effective for both GET and POST requests

        # former request syntax is msgpack=true

        res = self.request('gene/1017').json()
        res2 = self.msgpack_ok(self.request("gene/1017?format=msgpack").content)
        ok_(res, res2)

        res = self.request('query/?q=cdk').json()
        res2 = self.msgpack_ok(self.request("query/?q=cdk&format=msgpack").content)
        ok_(res, res2)

        res = self.request('metadata').json()
        res2 = self.msgpack_ok(self.request("metadata?format=msgpack").content)
        ok_(res, res2)

    def test_502_kwargs(self):
        ''' KWARGS CTRL Raw '''
        raw1 = self.request('gene/1017?raw=1').json()
        rawtrue = self.request('gene/1017?raw=true').json()
        raw0 = self.request('gene/1017?raw=0').json()
        rawfalse = self.request('gene/1017?raw=false').json()
        eq_(sorted(raw1), sorted(rawtrue))
        raw0.pop("_score", None)
        rawfalse.pop("_score", None)
        eq_(raw0, rawfalse)
        assert "_shards" in raw1
        assert "_shards" not in raw0
        assert "timed_out" in raw1
        assert "timed_out" not in raw0
        # query
        raw1 = self.request("query?q=ccnk&raw=1&size=3").json()
        rawtrue = self.request("query?q=ccnk&raw=true&size=3").json()
        raw0 = self.request("query?q=ccnk&raw=0&size=3").json()
        rawfalse = self.request("query?q=ccnk&raw=false&size=3").json()
        # this may vary so remove in comparison
        for res in [raw1, rawtrue, raw0, rawfalse]:
            del res["took"]
        # score should be the same. approx... so remove
        for res in [raw1, rawtrue]:
            for hit in res["hits"]["hits"]:
                del hit["_score"]
            del res["hits"]["max_score"]
        for res in [raw0, rawfalse]:
            for hit in res["hits"]:
                del hit["_score"]
            del res["max_score"]
        eq_(raw1, rawtrue)
        eq_(raw0, rawfalse)
        assert "_shards" in raw1
        assert "_shards" not in raw0

    def test_503_kwargs(self):
        ''' KWARGS ES Filtering '''
        # Aliases: _source, fields, filter
        # Endpoints: annotation, query
        # Methods: GET, POST

        res = self.request('gene/1017?fields=symbol,name,entrezgene').json()
        eq_(set(res), set(['_id', '_score', 'symbol', 'name', 'entrezgene']))
        res = self.request('gene/1017?filter=symbol,go.MF').json()
        eq_(set(res), set(['_id', '_score', 'symbol', 'go']))
        assert "MF" in res["go"]

    def test_504_kwargs(self):
        ''' KWARGS TRANSFROM Dotfield '''
        # query service
        # default dotfield=0
        rdefault = self.request("query?q=ccnk&fields=refseq.rna&size=3").json()
        # force no dotfield
        rfalse = self.request("query?q=ccnk&fields=refseq.rna&dotfield=false&size=3").json()
        # force dotfield
        rtrue = self.request("query?q=ccnk&fields=refseq.rna&dotfield=true&size=3").json()
        # check defaults and bool params
        # TODO: put this in json_ok as post-process filter ?
        for res in [rdefault, rfalse, rtrue]:
            for hit in res["hits"]:
                del hit["_score"]
        eq_(rdefault["hits"], rfalse["hits"])
        # check struct
        assert "refseq.rna" in rtrue["hits"][0].keys()
        assert "refseq" in rdefault["hits"][0].keys()
        assert "rna" in rdefault["hits"][0]["refseq"].keys()
        # TODO: no fields but dotfield => dotfield results
        # TODO: fields with dot but no dotfield => dotfield results

        # /gene service
        rdefault = self.request("gene/1017?filter=symbol,go.MF").json()
        rtrue = self.request("gene/1017?filter=symbol,go.MF&dotfield=true").json()
        rfalse = self.request("gene/1017?filter=symbol,go.MF&dotfield=false").json()
        # sharding makes scoring slightly variable
        rdefault.pop("_score")
        rfalse.pop("_score")
        eq_(rdefault, rfalse)
        assert "go.MF.term" in rtrue.keys()
        assert "go" in rdefault.keys()
        assert "MF" in rdefault["go"].keys()

    def test_505_kwargs(self):
        ''' KWARGS TRANSFORM Always_list and Allow_null '''
        res = self.request('gene/1017?always_list=entrezgene&allow_null=test.test2').json()
        assert 'entrezgene' in res
        assert isinstance(res['entrezgene'], list)
        assert 'test' in res
        assert 'test2' in res['test']
        assert res['test']['test2'] is None

    def test_601_hg19(self):
        ''' DATAFIELD Genome Assemblies Human 'hg19' '''

        url = 'query?q=hg19.chr12:57,795,963-57,815,592&species=human'
        res = self.request(url).json()

        ok_(len(res['hits']) == 2)
        ok_('_id' in res['hits'][0])
        url = 'query?q=chr12:57,795,963-57,815,592&species=human'
        res2 = self.request(url).json()
        ok_(res['total'] != res2['total'])

        url = 'gene/10017?fields=genomic_pos_hg19,exons_hg19'
        res = self.request(url).json()
        ok_('genomic_pos_hg19' in res)
        ok_('exons_hg19' in res)

    def test_602_mm9(self):
        ''' DATAFIELD Genome Assemblies Mouse 'mm9' '''
        url = 'query?q=mm9.chr12:57,795,963-57,815,592&species=mouse'
        res = self.request(url).json()
        ok_(len(res['hits']) == 2)
        ok_('_id' in res['hits'][0])
        url = 'query?q=chr12:57,795,963-57,815,592&species=mouse'
        res2 = self.request(url).json()
        ok_(res['total'] != res2['total'])
        url = 'gene/12049?fields=genomic_pos_mm9,exons_mm9'
        res = self.request(url).json()
        ok_('genomic_pos_mm9' in res)
        ok_('exons_mm9' in res)

    def test_603_refseq(self):
        ''' DATAFIELD Refseq '''
        protein = self.filter_hits(self.request("query?q=refseq:NP_001670&fields=refseq").json())
        url = "query?q=refseq:NM_001679&fields=refseq"
        rna = self.filter_hits(self.request(url).json())
        genomic = self.filter_hits(self.request("query?q=refseq:NT_005612&fields=refseq").json())
        url = "query?q=refseq.protein:NP_001670&fields=refseq"
        explicit_protein = self.filter_hits(self.request(url).json())
        self.filter_hits(explicit_protein)
        url = "query?q=refseq.rna:NM_001679&fields=refseq"
        explicit_rna = self.filter_hits(self.request(url).json())
        eq_(protein["hits"], explicit_protein["hits"])
        eq_(rna["hits"], explicit_rna["hits"])
        eq_(protein["hits"], rna["hits"])  # same result whatever the query
        eq_(genomic["hits"], [])  # genomic not indexed
        eq_(rna["total"], 1)
        hit = rna["hits"][0]
        eq_(hit["refseq"]["protein"], "NP_001670.1")
        assert hit["refseq"]["rna"].startswith("NM_001679.")

    def test_604_accession(self):
        ''' DATAFIELD Accession '''
        protein = self.filter_hits(self.request(
            "query?q=accession:AAH68303&fields=accession").json())
        rna = self.filter_hits(self.request("query?q=accession:BC068303&fields=accession").json())
        genomic = self.filter_hits(self.request(
            "query?q=accession:FJ497232&fields=accession").json())
        url = "query?q=accession.protein:AAH68303&fields=accession"
        explicit_protein = self.filter_hits(self.request(url).json())
        url = "query?q=accession.rna:BC068303&fields=accession"
        explicit_rna = self.filter_hits(self.request(url).json())
        eq_(protein["hits"], explicit_protein["hits"])
        eq_(rna["hits"], explicit_rna["hits"])
        eq_(protein["hits"], rna["hits"])  # same result whatever the query
        eq_(genomic["hits"], [])  # genomic not indexed
        eq_(rna["total"], 1)
        hit = rna["hits"][0]
        assert "AAH68303.1" in hit["accession"]["protein"]
        assert "BC068303.1" in hit["accession"]["rna"]

    def test_605_accession(self):
        ''' DATAFIELD Reporter '''
        human = self.filter_hits(self.request("query?q=reporter:2842429&fields=reporter").json())
        mouse = self.filter_hits(self.request(
            "query?q=reporter:1452128_a_at&fields=reporter").json())
        rat = self.filter_hits(self.request("query?q=reporter:1387540_at&fields=reporter").json())
        # human
        eq_(human["total"], 3)
        eq_(human["hits"][0]["reporter"]["HuGene-1_1"], "8110147")
        assert "2889211" in human["hits"][0]["reporter"]["HuEx-1_0"]
        assert "TC05002114.hg.1" in human["hits"][0]["reporter"]["HTA-2_0"]
        eq_(human["hits"][0]["reporter"]["HG-U133_Plus_2"], "228805_at")
        assert "gnf1h08801_at" in human["hits"][0]["reporter"]["GNF1H"]
        eq_(human["hits"][0]["reporter"]["HuGene-1_1"], "8110147")
        eq_(human["hits"][0]["reporter"]["HuGene-2_1"], "16992761")
        # rat
        eq_(rat["total"], 1)
        eq_(rat["hits"][0]["reporter"]["RaEx-1_0"], "7082865")
        eq_(rat["hits"][0]["reporter"]["Rat230_2"], "1387540_at")
        eq_(rat["hits"][0]["reporter"]["RaGene-2_1"], "17661681")
        eq_(rat["hits"][0]["reporter"]["RaGene-1_1"], "10747640")
        assert "AF036760_at" in rat["hits"][0]["reporter"]["RG-U34A"]
        # rat
        eq_(mouse["total"], 1)
        assert "1456141_x_at" in mouse["hits"][0]["reporter"]["Mouse430_2"]
        eq_(mouse["hits"][0]["reporter"]["MTA-1_0"], "TC0X00000742.mm.1")
        assert "165150_i_at" in mouse["hits"][0]["reporter"]["MG-U74Bv2"]
        eq_(mouse["hits"][0]["reporter"]["MoEx-1_0"], "7012082")
        eq_(mouse["hits"][0]["reporter"]["GNF1M"], "gnf1m11626_at")
        eq_(mouse["hits"][0]["reporter"]["MoGene-2_1"], "17535957")
        eq_(mouse["hits"][0]["reporter"]["MoGene-1_1"], "10600512")

    def test_606_accession(self):
        ''' DATAFIELD Interpro '''
        res = self.request(
            "query?q=interpro:IPR008389&fields=interpro&species=human,mouse,rat").json()
        eq_(res["total"], 6)
        assert set([pro["id"] for hit in res["hits"]
                    for pro in hit["interpro"]]) == set(['IPR008389',
                                                         'IPR017385'])

    def test_607_go(self):
        ''' DATAFIELD Go '''
        res = self.request("query?q=GO:0016324&fields=go&sort=_id").json()
        assert res["total"] > 800, \
            "Total is {}, should more than 800".format(res["total"])

    def test_608_homologene(self):
        ''' DATAFIELD Homologene '''
        res = self.request(
            "query?q=homologene:44221&fields=homologene&species=human,mouse,rat").json()
        eq_(res["total"], 3)
        hit = res["hits"][0]
        assert set([i[0] for i in hit["homologene"]["genes"]]) == \
            set([7955, 8364, 9031, 9598, 9606, 9615, 9913, 10090, 10116])

    def test_609_reagent(self):
        ''' DATAFIELD Reagent '''
        res = self.request("query?q=reagent:GNF190467&fields=reagent").json()
        eq_(res["total"], 1)
        hit = res["hits"][0]
        assert {"relationship": "is", "id": "GNF168655"} in \
            hit["reagent"]["GNF_Qia_hs-genome_v1_siRNA"]
        assert {"relationship": "is", "id": "GNF277345"} in \
            hit["reagent"]["GNF_mm+hs-MGC"]
        assert {"relationship": "is", "id": "GNF110093"} in \
            hit["reagent"]["NOVART_hs-genome_siRNA"]

    def test_610_refseq(self):
        ''' DATAFIELD Refseq '''
        # no version, _all
        res = self.filter_hits(self.request("query?q=NM_001798&fields=refseq").json())
        hits = res["hits"]
        eq_(len(hits), 1)
        found = False
        for rna in hits[0]["refseq"]["rna"]:
            if rna.startswith("NM_001798."):
                found = True
                break
        assert found
        # with version, _all
        sameres = self.filter_hits(self.request("query?q=NM_001798.5&fields=refseq").json())
        assert sameres["hits"] == res["hits"]
        # using protein ID
        sameres = self.filter_hits(self.request("query?q=XP_011536034&fields=refseq").json())
        assert sameres["hits"] == res["hits"]
        # using explicit field
        sameres = self.filter_hits(self.request("query?q=refseq:XP_011536034&fields=refseq").json())
        assert sameres["hits"] == res["hits"]

    def test_611_exac(self):
        ''' DATAFIELD ExAC '''
        # (Exome Aggregation Consortium)
        res = self.filter_hits(self.request(
            "query?q=exac.transcript:ENST00000266970.4&fields=exac").json())
        resnover = self.filter_hits(self.request(
            "query?q=exac.transcript:ENST00000266970&fields=exac").json())
        eq_(res["hits"], resnover["hits"])
        eq_(len(res["hits"]), 1)
        hit = res["hits"][0]
        eq_(hit["exac"]["bp"], 897)
        eq_(hit["exac"]["cds_end"], 56365409)
        eq_(hit["exac"]["cds_start"], 56360792)
        eq_(hit["exac"]["n_exons"], 7)
        eq_(hit["exac"]["transcript"], "ENST00000266970.4")
        eq_(hit["exac"]["all"]["mu_syn"], 0.00000345583178284)
        eq_(hit["exac"]["nonpsych"]["syn_z"], 0.0369369403215127)
        eq_(hit["exac"]["nontcga"]["mu_mis"], 0.00000919091133625)

    def test_612_other_names(self):
        ''' DATAFIELD Other_names '''
        # this one has some
        res = self.request("gene/107924918").json()
        assert "other_names" in res, "No other_names found in %s" % res
        eq_(res["other_names"], ['aquaporin NIP1-2-like',
                                 'aquaporin NIP1;2', 'aquaporin NIP1;3'])
        # that one not
        res = self.request("gene/1246509").json()
        assert not "other_names" in res
        # query by other_names:
        res = self.request("query?q=other_names:p33&size=50").json()
        assert res["total"] > 30  # currently 35...
        # eq_(len(res["hits"]),10)
        ids = [h["_id"] for h in res["hits"]]
        assert "1017" in ids, "Should have 1017 in results"

    def test_613_uniprot(self):
        ''' DATAFIELD Uniprot '''
        swissid = self.filter_hits(self.request("query?q=uniprot:Q8NEB7&fields=uniprot").json())
        trembid = self.filter_hits(self.request("query?q=uniprot:F5H2C2&fields=uniprot").json())
        eq_(swissid["hits"], trembid["hits"])
        eq_(trembid["total"], 1)
        eq_(trembid["hits"][0]["uniprot"]["Swiss-Prot"], "Q8NEB7")
        assert set(trembid["hits"][0]["uniprot"]["TrEMBL"]), \
            set(["E7EP66", "F5H2C2", "F5H3P4", "F5H5S8"])

    def test_614_ensembl(self):
        ''' DATAFIELD Ensembl Vertebrate '''
        url = "query?q=ensemblprotein:ENSP00000379391&fields=ensembl"
        prot = self.request(url).json()
        url = "query?q=ensembltranscript:ENST00000396082&fields=ensembl"
        rna = self.request(url).json()
        url = "query?q=ensemblgene:ENSG00000100373&fields=ensembl"
        gene = self.request(url).json()
        # don' compare score, useless
        for res in [prot, rna, gene]:
            res["hits"][0].pop("_score")
        eq_(prot["hits"], rna["hits"])
        eq_(rna["hits"], gene["hits"])
        eq_(rna["total"], 1)
        hit = rna["hits"][0]
        eq_(hit["ensembl"]["gene"], "ENSG00000100373")
        assert "ENSP00000216211" in hit["ensembl"]["protein"]
        assert "ENST00000216211" in hit["ensembl"]["transcript"]
        # POST /gene batch
        resl = self.request("gene", method='POST', data={'ids': 'ENSG00000148795'}).json()
        eq_(len(resl), 1)
        res = resl[0]
        eq_(res["_id"], "1586")

    def test_615_ensembl_additional(self):
        ''' DATAFIELD Ensembl Others
        Asserts the existance of the 4 other ensembl sources,
        by querying unique genes in each individual databases '''

        # Added in March 2019

        plant = "g00297"
        fungi = "ACLA_057550"
        metazoa = "ADAC005537"
        protists = "ALNC14_077170"
        sample_list = [plant, fungi, metazoa, protists]

        for sample in sample_list:
            self.query(q="ensembl.gene:" + sample, fields="ensembl")

    def test_616_pantherdb(self):
        ''' DATAFIELD Panther '''
        res = self.request("gene/348158?fields=pantherdb").json()
        assert "pantherdb" in res
        eq_(type(res["pantherdb"]["ortholog"]), list)
        res = self.request(
            "query?q=pantherdb.ortholog.taxid:10090%20AND%20pantherdb.uniprot_kb:O95867").json()
        eq_(len(res["hits"]), 1)
        eq_(res["hits"][0]["_id"], "80740")

    def test_617_pharos(self):
        ''' DATAFIELD Pharos '''
        # https://pharos.nih.gov/idg/about
        res = self.request("gene/56141?fields=pharos").json()
        eq_(res["pharos"]["target_id"], 4745)


if __name__ == '__main__':
    print()
    print('MyGene Remote Test:', MyGeneRemoteTest.host)
    print('-'*70)
    runmodule(argv=['', '--logging-level=INFO', '-v'])
