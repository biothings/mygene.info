''' MyGene Data-Aware Tests
    > python tests.py
'''

import os
import random

from nose.core import runmodule
from nose.tools import eq_, ok_

from biothings.tests import BiothingsTestCase


class MyGeneRemoteTest(BiothingsTestCase):
    ''' Test against server specified in environment variable MG_HOST
        or MyGene.info production server if MG_HOST is not specified
        MG_HOST must start with its protocol like http://mygene.info '''

    __test__ = True

    host = os.getenv("MG_HOST", "http://mygene.info").rstrip('/')
    api = '/v3'

    def filter_hits(self, dic, field=None):
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

    def test_00(self):
        ''' Connection to host server '''
        self.request(self.host)

    def test_01_gene(self):
        ''' All datasource fields '''

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

        res = self.request('gene/12566').json()
        attr = 'MGI'
        assert attr in res, 'Missing field "{}" in gene "12566"'.format(attr)

        res = self.request('gene/245962').json()
        attr = 'RGD'
        assert attr in res, 'Missing field "{}" in gene "245962"'.format(attr)

        res = self.request('gene/493498').json()
        attr = 'Xenbase'
        assert attr in res, 'Missing field "{}" in gene "493498"'.format(attr)

        res = self.request('gene/406715').json()
        attr = 'ZFIN'
        assert attr in res, 'Missing field "{}" in gene "406715"'.format(attr)

        res = self.request('gene/824036').json()
        attr = 'TAIR'
        assert attr in res, 'Missing field "{}" in gene "824036"'.format(attr)

        res = self.request('gene/42453').json()
        attr = 'FLYBASE'
        assert attr in res, 'Missing field "{}" in gene "42453"'.format(attr)

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

    def test_02_query_get(self):
        ''' GET query '''

        # public query api at query via get
        self.query(q='cdk2')
        self.query(q='GO:0004693')
        self.query(q='reporter:211803_at')
        self.query(q='IPR008351')
        self.query(q='hsa-mir-503')
        self.query(q='hsa-miR-503')

        # test fielded query
        self.query(q='symbol:cdk2')
        # test interval query
        self.query(q='chr1:151,073,054-151,383,976&species=human')

        con = self.request('query?q=cdk2&callback=mycallback').content
        assert con.startswith(b'mycallback(')

        # testing non-ascii character
        res = self.query(q='54097\xef\xbf\xbd\xef\xbf\xbdmouse', expect_hit=False)
        eq_(res['hits'], [])

        self.request('query', expect_status=400)

        self.request('query?q=tRNA:Y1:85Ae', expect_status=400)

        # ensure returned fields by default
        res = self.request('query?q=cdk').json()
        idx = random.randrange(0, 10)  # pick one
        deffields = res["hits"][idx].keys()  # pick one...
        expected = ["_id", "_score", "taxid", "entrezgene", "name", "symbol"]
        assert sorted(list(deffields)) == sorted(expected), \
            "%s != %s" % (sorted(list(deffields)), sorted(expected))

    def test_03_query_post(self):
        ''' POST query '''

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

    def test_04_query_get_interval(self):
        ''' GET query with interval '''
        self.query(q='chr1:1000-100000', species='human')

    def test_05_query_get_size(self):
        ''' GET query with size '''
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

    def test_06_gene(self):
        ''' GET gene '''
        res = self.request('gene/1017').json()
        eq_(res['entrezgene'], "1017")

        # testing non-ascii character
        self.request('gene/54097\xef\xbf\xbd\xef\xbf\xbdmouse', expect_status=404)

        # one test has been removed here as dot in the geneid is no more supported

        # testing filtering parameters
        res = self.request('gene/1017?fields=symbol,name,entrezgene').json()
        eq_(set(res), set(['_id', '_score', 'symbol', 'name', 'entrezgene']))
        res = self.request('gene/1017?filter=symbol,go.MF').json()
        eq_(set(res), set(['_id', '_score', 'symbol', 'go']))
        assert "MF" in res["go"]

        self.request('gene', expect_status=404)
        self.request('gene/', expect_status=404)

    def test_07_gene(self):
        ''' POST gene '''
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
        eq_(set(res[0].keys()), set(default_fields),
            msg='set(1017.keys())!=set(default_fields)')
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

    def test_08_status(self):
        ''' Status response '''
        self.request('/status')
        self.request('/status', method='HEAD')

    def test_09_metadata(self):
        ''' GET metadata '''
        root = self.request('/metadata').json()
        v3 = self.request('metadata').json()
        eq_(root, v3, msg='res({})!=res({})'.format(
            self.host + '/metadata', self.host + self.api + '/metadata'))
        available_fields = ['available_fields', 'src_version', 'build_version',
                            'app_revision', 'build_date', 'taxonomy',
                            'stats', 'genome_assembly', 'src', 'source', 'biothing_type']
        eq_(set(root.keys()), set(available_fields))
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

    def test_10_gene_always_list_allow_null(self):
        ''' GET gene with always_list and allow_null '''
        res = self.request('gene/1017?always_list=entrezgene&allow_null=test.test2').json()
        assert 'entrezgene' in res
        assert isinstance(res['entrezgene'], list)
        assert 'test' in res
        assert 'test2' in res['test']
        assert res['test']['test2'] is None

    def test_query_facets(self):
        ''' GET query with facets '''
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

        u = 'query?q=cdk?&facets=taxid&species_facet_filter=human&species=human,mouse,rat'
        res2 = self.request(u).json()
        eq_(res2['facets']['taxid']['total'], res['total'])
        eq_(res2['facets']['taxid'], res['facets']['taxid'])
        eq_([x["count"] for x in res2['facets']['taxid']['terms']
             if x["term"] == 9606][0], res2['total'])

    def test_query_userquery(self):
        ''' GET query with userquery '''
        res1 = self.request('query?q=cdk').json()
        res2 = self.request("query?q=cdk&userquery=bgood_cure_griffith").json()
        ok_(res1['total'] > res2['total'])

        # nonexisting user filter gets ignored
        res2 = self.request("query?q=cdk&userquery=aaaa").json()
        eq_(res1['total'], res2['total'])

    def test_existsfilter(self):
        ''' GET query with exists '''
        res1 = self.request('query?q=cdk').json()
        res2 = self.request("query?q=cdk&exists=pharmgkb").json()
        ok_(res1['total'] > res2['total'])
        res3 = self.request("query?q=cdk&exists=pharmgkb,pdb").json()
        ok_(res2['total'] > res3['total'])

    def test_missingfilter(self):
        ''' GET query with missing '''
        res1 = self.request('query?q=cdk').json()
        res2 = self.request('query?q=cdk&missing=pdb').json()
        ok_(res1['total'] > res2['total'])
        res3 = self.request("query?q=cdk&missing=pdb,MIM").json()
        ok_(res2['total'] > res3['total'])

    def test_unicode(self):
        ''' Unicode query string '''
        s = u'基因'

        self.request('gene/' + s, expect_status=404)

        res = self.request("gene", method='POST', data={'ids': s}).json()
        eq_(res[0]['notfound'], True)
        eq_(len(res), 1)
        res = self.request("gene", method='POST', data={'ids': '1017, ' + s}).json()
        eq_(res[1]['notfound'], True)
        eq_(len(res), 2)

        res = self.query(q=s, expect_hit=False)
        eq_(res['hits'], [])

        res = self.query(method='POST', q=s, scopes='symbol', expect_hit=False)
        eq_(res[0]['notfound'], True)
        eq_(len(res), 1)

        res = self.query(method='POST', q='cdk2+' + s, expect_hit=False)
        eq_(res[1]['notfound'], True)
        eq_(len(res), 2)

    def test_hg19(self):
        ''' hg19 records '''
        u = 'query?q=hg19.chr12:57,795,963-57,815,592&species=human'
        res = self.request(u).json()

        ok_(len(res['hits']) == 2)
        ok_('_id' in res['hits'][0])
        u = 'query?q=chr12:57,795,963-57,815,592&species=human'
        res2 = self.request(u).json()
        ok_(res['total'] != res2['total'])

        u = 'gene/10017?fields=genomic_pos_hg19,exons_hg19'
        res = self.request(u).json()
        ok_('genomic_pos_hg19' in res)
        ok_('exons_hg19' in res)

    def test_mm9(self):
        ''' mm9 records '''
        u = 'query?q=mm9.chr12:57,795,963-57,815,592&species=mouse'
        res = self.request(u).json()
        ok_(len(res['hits']) == 2)
        ok_('_id' in res['hits'][0])
        u = 'query?q=chr12:57,795,963-57,815,592&species=mouse'
        res2 = self.request(u).json()
        ok_(res['total'] != res2['total'])
        u = 'gene/12049?fields=genomic_pos_mm9,exons_mm9'
        res = self.request(u).json()
        ok_('genomic_pos_mm9' in res)
        ok_('exons_mm9' in res)

    def test_msgpack(self):
        ''' msgpack output '''
        res = self.request('gene/1017').json()
        res2 = self.msgpack_ok(self.request("gene/1017?msgpack=true").content)
        ok_(res, res2)

        res = self.request('query/?q=cdk').json()
        res2 = self.msgpack_ok(self.request("query/?q=cdk&msgpack=true").content)
        ok_(res, res2)

        res = self.request('metadata').json()
        res2 = self.msgpack_ok(self.request("metadata?msgpack=true").content)
        ok_(res, res2)

    def test_taxonomy(self):
        ''' taxonomy '''
        res = self.request('species/1239').json()
        ok_("lineage" in res)

        res = self.request("species/46170?include_children=true").json()
        ok_(len(res['children']) >= 305)

        res2 = self.request("species/46170?include_children=true&has_gene=1").json()
        ok_(len(res2['children']) >= 16)
        ok_(len(res2['children']) <= len(res['children']))

        u = 'query?q=lytic%20enzyme&species=1386&include_tax_tree=true'
        res = self.request(u).json()
        ok_(res['total'] >= 2)
        res2 = self.request("query?q=lytic%20enzyme&species=1386").json()
        eq_(res2['total'], 0)

    def test_static(self):
        ''' Static content serving '''
        self.request('/favicon.ico')
        self.request('/robots.txt')

    def test_fetch_all(self):
        ''' GET query with fetch_all '''
        res = self.request("query?q=cdk*&species=all&fetch_all=true").json()
        assert '_scroll_id' in res

        res2 = self.query(scroll_id=res['_scroll_id'])
        assert 'hits' in res2
        ok_(len(res2['hits']) >= 2)

    def test_list_handling(self):
        ''' GET query with fetch_all '''
        res = self.request("query", method='POST',
                           data={'q': '"cyclin dependent kinase 2", "cyclin dependent kinase 3"',
                                 'scopes': 'name', 'fields': 'entrezgene,  name',
                                 'species': 'human'}).json()
        query_set = {l['query'] for l in res}
        # make sure queries are interpreted correctly and returned
        assert query_set == set(
            ["cyclin dependent kinase 2", "cyclin dependent kinase 3"])
        # make sure fields are interpreted correctly
        field_set = set()
        for l in res:
            if 'entrezgene' in l:
                field_set.add('entrezgene')
            if 'name' in l:
                field_set.add('name')
        assert field_set == set(['entrezgene', 'name'])

    def test_dotfield(self):
        ''' dotfield support '''
        # query service
        # default dotfield=0
        rdefault = self.request("query?q=ccnk&fields=refseq.rna&size=3").json()
        # force no dotfield
        rfalse = self.request("query?q=ccnk&fields=refseq.rna&dotfield=false&size=3").json()
        # force dotfield
        rtrue = self.request("query?q=ccnk&fields=refseq.rna&dotfield=true&size=3").json()
        # check defaults and bool params
        # TODO: put this in json_ok as post-process filter ?
        for d in [rdefault, rfalse, rtrue]:
            for h in d["hits"]:
                del h["_score"]
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

    def test_raw(self):
        ''' raw support '''
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
        for d in [raw1, rawtrue, raw0, rawfalse]:
            del d["took"]
        # score should be the same. approx... so remove
        for d in [raw1, rawtrue]:
            for h in d["hits"]["hits"]:
                del h["_score"]
            del d["hits"]["max_score"]
        for d in [raw0, rawfalse]:
            for h in d["hits"]:
                del h["_score"]
            del d["max_score"]
        eq_(raw1, rawtrue)
        eq_(raw0, rawfalse)
        assert "_shards" in raw1
        assert "_shards" not in raw0

    def test_species(self):
        ''' GET species '''
        dic = self.request("species/9606").json()
        eq_(set(dic.keys()), set(['taxid', 'authority', 'lineage', '_id',
                                  'common_name', 'genbank_common_name',
                                  '_version', 'parent_taxid', 'scientific_name',
                                  'has_gene', 'children', 'rank',
                                  'uniprot_name']))

    def test_query_dotstar_refseq(self):
        ''' refseq.* '''
        protein = self.filter_hits(self.request("query?q=refseq:NP_001670&fields=refseq").json())
        u = "query?q=refseq:NM_001679&fields=refseq"
        rna = self.filter_hits(self.request(u).json())
        genomic = self.filter_hits(self.request("query?q=refseq:NT_005612&fields=refseq").json())
        u = "query?q=refseq.protein:NP_001670&fields=refseq"
        explicit_protein = self.filter_hits(self.request(u).json())
        self.filter_hits(explicit_protein)
        u = "query?q=refseq.rna:NM_001679&fields=refseq"
        explicit_rna = self.filter_hits(self.request(u).json())
        eq_(protein["hits"], explicit_protein["hits"])
        eq_(rna["hits"], explicit_rna["hits"])
        eq_(protein["hits"], rna["hits"])  # same result whatever the query
        eq_(genomic["hits"], [])  # genomic not indexed
        eq_(rna["total"], 1)
        hit = rna["hits"][0]
        eq_(hit["refseq"]["protein"], "NP_001670.1")
        eq_(hit["refseq"]["rna"], "NM_001679.4")  # TODO

    def test_query_dotstar_accession(self):
        ''' accession.* '''
        protein = self.filter_hits(self.request(
            "query?q=accession:AAH68303&fields=accession").json())
        rna = self.filter_hits(self.request("query?q=accession:BC068303&fields=accession").json())
        genomic = self.filter_hits(self.request(
            "query?q=accession:FJ497232&fields=accession").json())
        u = "query?q=accession.protein:AAH68303&fields=accession"
        explicit_protein = self.filter_hits(self.request(u).json())
        u = "query?q=accession.rna:BC068303&fields=accession"
        explicit_rna = self.filter_hits(self.request(u).json())
        eq_(protein["hits"], explicit_protein["hits"])
        eq_(rna["hits"], explicit_rna["hits"])
        eq_(protein["hits"], rna["hits"])  # same result whatever the query
        eq_(genomic["hits"], [])  # genomic not indexed
        eq_(rna["total"], 1)
        hit = rna["hits"][0]
        assert "AAH68303.1" in hit["accession"]["protein"]
        assert "BC068303.1" in hit["accession"]["rna"]

    def test_query_dotstar_reporter(self):
        ''' reporter '''
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

    def test_query_dotstar_interpro(self):
        ''' interpro '''
        res = self.request(
            "query?q=interpro:IPR008389&fields=interpro&species=human,mouse,rat").json()
        eq_(res["total"], 6)
        assert set([pro["id"] for hit in res["hits"]
                    for pro in hit["interpro"]]) == set(['IPR008389',
                                                         'IPR017385'])

    def test_query_dotstar_go(self):
        ''' go '''
        res = self.request("query?q=GO:0016324&fields=go&sort=_id").json()
        assert res["total"] > 800, \
            "Total is {}, should more than 800".format(res["total"])

    def test_query_dotstar_homologene(self):
        ''' homologene '''
        res = self.request(
            "query?q=homologene:44221&fields=homologene&species=human,mouse,rat").json()
        eq_(res["total"], 3)
        h = res["hits"][0]
        assert set([i[0] for i in h["homologene"]["genes"]]) == \
            set([7955, 8364, 9031, 9598, 9606, 9615, 9913, 10090, 10116])

    def test_query_dotstar_reagent(self):
        ''' reagent '''
        res = self.request("query?q=reagent:GNF190467&fields=reagent").json()
        eq_(res["total"], 1)
        hit = res["hits"][0]
        assert {"relationship": "is", "id": "GNF168655"} in \
            hit["reagent"]["GNF_Qia_hs-genome_v1_siRNA"]
        assert {"relationship": "is", "id": "GNF277345"} in \
            hit["reagent"]["GNF_mm+hs-MGC"]
        assert {"relationship": "is", "id": "GNF110093"} in \
            hit["reagent"]["NOVART_hs-genome_siRNA"]

    def test_query_dotstar_uniprot(self):
        ''' uniport '''
        swissid = self.filter_hits(self.request("query?q=uniprot:Q8NEB7&fields=uniprot").json())
        trembid = self.filter_hits(self.request("query?q=uniprot:F5H2C2&fields=uniprot").json())
        eq_(swissid["hits"], trembid["hits"])
        eq_(trembid["total"], 1)
        eq_(trembid["hits"][0]["uniprot"]["Swiss-Prot"], "Q8NEB7")
        assert set(trembid["hits"][0]["uniprot"]["TrEMBL"]), \
            set(["E7EP66", "F5H2C2", "F5H3P4", "F5H5S8"])

    def test_query_ensembl(self):
        ''' ensembl '''
        u = "query?q=ensemblprotein:ENSP00000379391&fields=ensembl"
        prot = self.request(u).json()
        u = "query?q=ensembltranscript:ENST00000396082&fields=ensembl"
        rna = self.request(u).json()
        u = "query?q=ensemblgene:ENSG00000100373&fields=ensembl"
        gene = self.request(u).json()
        # don' compare score, useless
        [d["hits"][0].pop("_score") for d in [prot, rna, gene]]
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

    def test_query_ensembl_additional(self):
        ''' ensembl+
        Asserts the existance of the 4 other ensembl sources,
        by querying unique genes in each individual databases '''

        query_string = "ensembl.gene:{}&fields=ensembl"

        plant = "g00297"
        fungi = "ACLA_057550"
        metazoa = "ADAC005537"
        protists = "ALNC14_077170"
        sample_list = [plant, fungi, metazoa, protists]

        for sample in sample_list:
            self.query(q=query_string.format(sample))

    def test_sort_by_fields(self):
        ''' sort by field '''
        res = self.request("query?q=MTFMT&sort=taxid&species=human,mouse,rat").json()
        hits = res["hits"]
        assert len(hits) == 3
        eq_(hits[0]["entrezgene"], "123263")
        eq_(hits[1]["entrezgene"], "69606")
        eq_(hits[2]["entrezgene"], "315763")

    def test_refseq_versioning(self):
        ''' refseq '''
        # no version, _all
        res = self.filter_hits(self.request("query?q=NM_001798&fields=refseq").json())
        hits = res["hits"]
        eq_(len(hits), 1)
        ok_("NM_001798.5" in hits[0]["refseq"]["rna"])  # TODO
        # with version, _all
        sameres = self.filter_hits(self.request("query?q=NM_001798.5&fields=refseq").json())
        assert sameres["hits"] == res["hits"]
        # using protein ID
        sameres = self.filter_hits(self.request("query?q=XP_011536034&fields=refseq").json())
        assert sameres["hits"] == res["hits"]
        # using explicit field
        sameres = self.filter_hits(self.request("query?q=refseq:XP_011536034&fields=refseq").json())
        assert sameres["hits"] == res["hits"]

    def test_disambiguate_ensembl_entrez_ids(self):
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
        # test "orphan" EntrezID (associated EnsemblIDs were all resolved into other EntrezIDs but we want to keep ambiguated
        # Ensembl data for those)
        # res = self.request("/gene/100287596"))
        ###ensids = [e["gene"] for e in res["ensembl"]]
        # eq_(set(endids),{"ENSG00000248472","ENSG00000223972"})

    def test_caseinsentive_datasources(self):
        self.query(q='mirbase:MI0017267')
        self.query(q='wormbase:WBGene00057218&species=31234')
        self.query(q='xenbase:XB-GENE-1001990&species=frog')
        self.query(q='Xenbase:XB-GENE-1001990&species=frog')
        self.query(q=r'mgi:MGI\\:104772')

    def test_exac(self):
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

    def test_caseinsensitive(self):
        # sometimes the orders of results are *slightly* different for cdk2 and CDK2
        # so limit to top 3 more stable results
        lower = self.filter_hits(self.request("query?q=cdk2&size=3").json())
        upper = self.filter_hits(self.request("query?q=CDK2&size=3").json())
        eq_(lower["hits"], upper["hits"])

    def test_symbolnamespecies_order(self):
        res = self.request("query?q=cdk2&species=human,mouse,rat").json()
        hits = res["hits"]
        # first is 1017, it's human and cdk2 is a symbol
        eq_(hits[0]["_id"], "1017")
        # second is 12566, mouse
        eq_(hits[1]["_id"], "12566")
        # third is 362817, rat
        eq_(hits[2]["_id"], "362817")

    def test_gene_other_names(self):
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

    def test_int_float(self):
        def check_homologene(res):
            for h in res["homologene"]["genes"]:
                eq_(type(h[0]), int)
                eq_(type(h[1]), int)

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

    def test_pantherdb(self):
        res = self.request("gene/348158?fields=pantherdb").json()
        assert "pantherdb" in res
        eq_(type(res["pantherdb"]["ortholog"]), list)
        res = self.request(
            "query?q=pantherdb.ortholog.taxid:10090%20AND%20pantherdb.uniprot_kb:O95867").json()
        eq_(len(res["hits"]), 1)
        eq_(res["hits"][0]["_id"], "80740")

    def test_pharos(self):
        res = self.request("gene/56141?fields=pharos").json()
        eq_(res["pharos"]["target_id"], 4745)


if __name__ == '__main__':
    runmodule(argv=['', '--logging-level=INFO', '-v'])
