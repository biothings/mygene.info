
from biothings.tests.tests import BiothingTestHelper, _d, _e
from biothings.tests.settings import NosetestSettings
from nose.tools import ok_, eq_

ns = NosetestSettings()


class MyGeneTest(BiothingTestHelper):
    __test__ = True # explicitly set this to be a test class
    # Add extra nosetests here
    pass

    #############################################################
    # Test functions                                            #
    #############################################################
    #@with_setup(setup_func, teardown_func)
    def test_main(self):
        #/
        self.get_ok(self.host)


    def test_gene_object(self):
        #test all fields are load in gene objects
        res = self.json_ok(self.get_ok(self.api + '/gene/1017'))

        attr_li = ['HGNC', 'HPRD', 'MIM', 'Vega', '_id', 'accession', 'alias',
                   'ec', 'ensembl', 'entrezgene', 'genomic_pos', 'go', 'homologene',
                   'interpro', 'ipi', 'map_location', 'name', 'pdb', 'pharmgkb', 'pir',
                   'prosite', 'reagent', 'refseq', 'reporter', 'summary', 'symbol',
                   'taxid', 'type_of_gene', 'unigene', 'uniprot', 'exons', 'generif']
        for attr in attr_li:
            assert res.get(attr, None) is not None, 'Missing field "{}" in gene "1017"'.format(attr)

        res = self.json_ok(self.get_ok(self.api + '/gene/12566'))
        attr = 'MGI'
        assert res.get(attr, None) is not None, 'Missing field "{}" in gene "12566"'.format(attr)

        res = self.json_ok(self.get_ok(self.api + '/gene/245962'))
        attr = 'RGD'
        assert res.get(attr, None) is not None, 'Missing field "{}" in gene "245962"'.format(attr)

        res = self.json_ok(self.get_ok(self.api + '/gene/493498'))
        attr = 'Xenbase'
        assert res.get(attr, None) is not None, 'Missing field "{}" in gene "493498"'.format(attr)

        res = self.json_ok(self.get_ok(self.api + '/gene/406715'))
        attr = 'ZFIN'
        assert res.get(attr, None) is not None, 'Missing field "{}" in gene "406715"'.format(attr)

        res = self.json_ok(self.get_ok(self.api + '/gene/824036'))
        attr = 'TAIR'
        assert res.get(attr, None) is not None, 'Missing field "{}" in gene "824036"'.format(attr)

        res = self.json_ok(self.get_ok(self.api + '/gene/42453'))
        attr = 'FLYBASE'
        assert res.get(attr, None) is not None, 'Missing field "{}" in gene "42453"'.format(attr)

        #pig
        res = self.json_ok(self.get_ok(self.api + '/gene/397593'))
        assert 'snowball' in res.get('reporter', {}), 'Missing field "reporter.snowball" in gene "397593"'

        #nematode
        res = self.json_ok(self.get_ok(self.api + '/gene/172677'))
        res = self.json_ok(self.get_ok(self.api + '/gene/9821293'))    # this is not nematode, "taxid": 31234
        attr = 'WormBase'
        assert res.get(attr, None) is not None, 'Missing field "{}" in gene "9821293"'.format(attr)

        #fission yeast
        res = self.json_ok(self.get_ok(self.api + '/gene/2539869'))

        #e coli.
        #res = self.json_ok(self.get_ok(self.api + '/gene/12931566'))

        #mirna
        res = self.json_ok(self.get_ok(self.api + '/gene/406881'))
        attr = 'miRBase'
        assert res.get(attr, None) is not None, 'Missing field "{}" in gene "406881"'.format(attr)


    #def has_hits(self,q):
    #    d = self.json_ok(self.get_ok(self.api + '/query?q='+q))
    #    ok_(d.get('total', 0) > 0 and len(d.get('hits', [])) > 0)


    def test_query(self):
        #public query api at /query via get
        # self.json_ok(self.get_ok(self.api + '/query?q=cdk2'))
        # self.json_ok(self.get_ok(self.api + '/query?q=GO:0004693'))
        # self.json_ok(self.get_ok(self.api + '/query?q=211803_at'))
        self.has_hits('cdk2')
        self.has_hits('GO:0004693')
        self.has_hits('211803_at')
        self.has_hits('IPR008351')
        self.has_hits('hsa-mir-503')
        self.has_hits('hsa-miR-503')

        #test fielded query
        self.has_hits('symbol:cdk2')
        #test interval query
        self.has_hits('chr1:151,073,054-151,383,976&species=human')

        con = self.get_ok(self.api + '/query?q=cdk2&callback=mycallback')
        ok_(con.startswith(b'mycallback('))

        # testing non-ascii character
        res = self.json_ok(self.get_ok(self.api + '/query?q=54097\xef\xbf\xbd\xef\xbf\xbdmouse'))
        eq_(res['hits'], [])

        res = self.json_ok(self.get_ok(self.api + '/query'), checkerror=False)
        assert 'error' in res

        res = self.json_ok(self.get_ok(self.api + '/query?q=tRNA:Y1:85Ae'), checkerror=False)
        assert 'error' in res


    def test_query_post(self):
        #/query via post
        self.json_ok(self.post_ok(self.api + '/query', {'q': '1017'}))

        res = self.json_ok(self.post_ok(self.api + '/query', {'q': '1017',
                                               'scopes': 'entrezgene'}))
        eq_(len(res), 1)
        eq_(res[0]['_id'], '1017')

        res = self.json_ok(self.post_ok(self.api + '/query', {'q': '211803_at,1018',
                                               'scopes': 'reporter,entrezgene'}))
        eq_(len(res), 2)
        eq_(res[0]['_id'], '1017')
        eq_(res[1]['_id'], '1018')

        res = self.json_ok(self.post_ok(self.api + '/query', {'q': 'CDK2',
                                               'species': 'human,10090,frog,pig',
                                               'scopes': 'symbol',
                                               'fields': 'name,symbol'}))
        assert len(res) >= 4, (res, len(res))
        res = self.json_ok(self.post_ok(self.api + '/query', {}), checkerror=False)
        assert 'error' in res, res

        res = self.json_ok(self.post_ok(self.api + '/query', {'q': '[1017, "1018"]',
                                               'scopes': 'entrezgene',
                                               'jsoninput': 'true'}))
        eq_(len(res), 2)
        eq_(res[0]['_id'], '1017')
        eq_(res[1]['_id'], '1018')


    def test_query_interval(self):
        res = self.json_ok(self.get_ok(self.api + '/query?q=chr1:1000-100000&species=human'))
        ok_(len(res['hits']) > 1)
        ok_('_id' in res['hits'][0])


    def test_query_size(self):
        res = self.json_ok(self.get_ok(self.api + '/query?q=cdk?'))
        eq_(len(res['hits']), 10)  # default is 10
        ok_(res['total'] > 10)

        res = self.json_ok(self.get_ok(self.api + '/query?q=cdk?&size=0'))
        eq_(len(res['hits']), 0)

        res = self.json_ok(self.get_ok(self.api + '/query?q=cdk?&limit=20'))
        eq_(len(res['hits']), 20)

        res1 = self.json_ok(self.get_ok(self.api + '/query?q=cdk?&from=0&size=20'))
        #res2 = self.json_ok(self.get_ok(self.api + '/query?q=cdk*&from=0&size=20'))
        res = self.json_ok(self.get_ok(self.api + '/query?q=cdk?&skip=10&size=20'))
        #eq_([x['_id'] for x in res1['hits']],[x['_id'] for x in res2['hits']])
        eq_(len(res['hits']), 20)
        #print res1['hits'].index(res['hits'][0])
        #print [x['_id'] for x in res1['hits']]
        #eq_(res['hits'][0], res1['hits'][10])
        assert res['hits'][0] in res1['hits']

        # API doc says cap 1000
        res = self.json_ok(self.get_ok(self.api + '/query?q=*&size=1000'))
        eq_(len(res['hits']), 1000)
        res = self.json_ok(self.get_ok(self.api + '/query?q=*&size=1001'))
        eq_(len(res['hits']), 1000)
        res = self.json_ok(self.get_ok(self.api + '/query?q=*&size=2000'))
        eq_(len(res['hits']), 1000)

        #assert 1==0
        res = self.json_ok(self.get_ok(self.api + '/query?q=cdk?&size=1a'), checkerror=False)  # invalid size parameter
        assert 'error' in res


    def test_gene(self):
        res = self.json_ok(self.get_ok(self.api + '/gene/1017'))
        eq_(res['entrezgene'], 1017)
        # testing non-ascii character
        self.get_404(self.api + '/gene/' + '54097\xef\xbf\xbd\xef\xbf\xbdmouse')

        # commented out this test, as no more
        #allow dot in the geneid
        #res = self.json_ok(self.get_ok(self.api + '/gene/Y105C5B.255'))

        # testing filtering parameters
        res = self.json_ok(self.get_ok(self.api + '/gene/1017?fields=symbol,name,entrezgene'))
        eq_(set(res), set(['_id', '_version', 'symbol', 'name', 'entrezgene']))
        res = self.json_ok(self.get_ok(self.api + '/gene/1017?filter=symbol,go.MF'))
        fout = open("bla","w")
        fout.write("%s" % res)
        fout.close()
        eq_(set(res), set(['_id', '_version', 'symbol', 'go']))
        assert "MF" in res["go"]
        #eq_(res['go'].keys(), ['MF'])

        self.get_404(self.api + '/gene')
        self.get_404(self.api + '/gene/')

        #res = self.json_ok(self.get_ok(self.api + '/boc/bgps/gene/1017'))
        #ok_('SpeciesList' in res)

    def test_gene_post(self):
        res = self.json_ok(self.post_ok(self.api + '/gene', {'ids': '1017'}))
        eq_(len(res), 1)
        eq_(res[0]['entrezgene'], 1017)

        res = self.json_ok(self.post_ok(self.api + '/gene', {'ids': '1017, 1018'}))
        eq_(len(res), 2)
        eq_(res[0]['_id'], '1017')
        eq_(res[1]['_id'], '1018')

        res = self.json_ok(self.post_ok(self.api + '/gene', {'ids': '1017,1018', 'fields': 'symbol,name,entrezgene'}))
        eq_(len(res), 2)
        for _g in res:
            eq_(set(_g), set(['_id', '_score', 'query', 'symbol', 'name', 'entrezgene']))

        res = self.json_ok(self.post_ok(self.api + '/gene', {'ids': '1017,1018', 'filter': 'symbol,go.MF'}))
        eq_(len(res), 2)
        for _g in res:
            eq_(set(_g), set(['_id', '_score', 'query', 'symbol', 'go']))
            assert "MF" in _g["go"]


    def test_status(self):
        #/status
        self.get_ok(self.host + '/status')
        self.head_ok(self.host + '/status')


    def test_metadata(self):
        root = self.json_ok(self.get_ok(self.host + '/metadata'))
        v2 = self.json_ok(self.get_ok(self.api + '/metadata'))
        eq_(root,v2)
        eq_(set(root.keys()),set(['available_fields', 'src_version', 'app_revision', 'timestamp', 'taxonomy',
            'stats','genome_assembly','source']))
        fields =self.json_ok(self.get_ok(self.api + '/metadata/fields'))
        # test random field
        assert "refseq" in fields
        assert "accession.rna" in fields
        assert "interpro.desc" in fields
        assert "homologene" in fields
        assert "reporter.snowball" in fields


    def test_query_facets(self):
        res = self.json_ok(self.get_ok(self.api + '/query?q=cdk?&facets=taxid'))
        ok_('facets' in res)
        ok_('taxid' in res['facets'])
        eq_(res['facets']['taxid']['total'], res['total'])
        eq_(res['facets']['taxid']['other'], 0)
        eq_(res['facets']['taxid']['missing'], 0)

        res2 = self.json_ok(self.get_ok(self.api + '/query?q=cdk?&facets=taxid&species_facet_filter=human'))
        eq_(res2['facets']['taxid']['total'], res['total'])
        eq_(res2['facets']['taxid'], res['facets']['taxid'])
        eq_([x["count"] for x in res2['facets']['taxid']['terms'] if x["term"] == 9606][0], res2['total'])


    def test_query_userfilter(self):
        res1 = self.json_ok(self.get_ok(self.api + '/query?q=cdk'))
        res2 = self.json_ok(self.get_ok(self.api + '/query?q=cdk&userfilter=bgood_cure_griffith'))
        ok_(res1['total'] > res2['total'])

        res2 = self.json_ok(self.get_ok(self.api + '/query?q=cdk&userfilter=aaaa'))   # nonexisting user filter gets ignored.
        eq_(res1['total'], res2['total'])


    def test_existsfilter(self):
        res1 = self.json_ok(self.get_ok(self.api + '/query?q=cdk'))
        res2 = self.json_ok(self.get_ok(self.api + '/query?q=cdk&exists=pharmgkb'))
        ok_(res1['total'] > res2['total'])
        res3 = self.json_ok(self.get_ok(self.api + '/query?q=cdk&exists=pharmgkb,pdb'))
        ok_(res2['total'] > res3['total'])


    def test_missingfilter(self):
        res1 = self.json_ok(self.get_ok(self.api + '/query?q=cdk'))
        res2 = self.json_ok(self.get_ok(self.api + '/query?q=cdk&missing=pdb'))
        ok_(res1['total'] > res2['total'])
        res3 = self.json_ok(self.get_ok(self.api + '/query?q=cdk&missing=pdb,MIM'))
        ok_(res2['total'] > res3['total'])


    def test_unicode(self):
        s = u'基因'

        self.get_404(self.api + '/gene/' + s)

        res = self.json_ok(self.post_ok(self.api + '/gene', {'ids': s}))
        eq_(res[0]['notfound'], True)
        eq_(len(res), 1)
        res = self.json_ok(self.post_ok(self.api + '/gene', {'ids': '1017, ' + s}))
        eq_(res[1]['notfound'], True)
        eq_(len(res), 2)

        res = self.json_ok(self.get_ok(self.api + '/query?q=' + s))
        eq_(res['hits'], [])

        res = self.json_ok(self.post_ok(self.api + '/query', {"q": s, "scopes": 'symbol'}))
        eq_(res[0]['notfound'], True)
        eq_(len(res), 1)

        res = self.json_ok(self.post_ok(self.api + '/query', {"q": 'cdk2+' + s}))
        eq_(res[1]['notfound'], True)
        eq_(len(res), 2)


    def test_hg19(self):
        res = self.json_ok(self.get_ok(self.api + '/query?q=hg19.chr12:57,795,963-57,815,592&species=human'))
        ok_(len(res['hits']) == 2)
        ok_('_id' in res['hits'][0])
        res2 = self.json_ok(self.get_ok(self.api + '/query?q=chr12:57,795,963-57,815,592&species=human'))
        ok_(res['total'] != res2['total'])

        res = self.json_ok(self.get_ok(self.api + '/gene/10017?fields=genomic_pos_hg19,exons_hg19'))
        ok_('genomic_pos_hg19' in res)
        ok_('exons_hg19' in res)


    def test_mm9(self):
        res = self.json_ok(self.get_ok(self.api + '/query?q=mm9.chr12:57,795,963-57,815,592&species=mouse'))
        ok_(len(res['hits']) == 2)
        ok_('_id' in res['hits'][0])
        res2 = self.json_ok(self.get_ok(self.api + '/query?q=chr12:57,795,963-57,815,592&species=mouse'))
        ok_(res['total'] != res2['total'])

        res = self.json_ok(self.get_ok(self.api + '/gene/12049?fields=genomic_pos_mm9,exons_mm9'))
        ok_('genomic_pos_mm9' in res)
        ok_('exons_mm9' in res)


    def test_msgpack(self):
        res = self.json_ok(self.get_ok(self.api + '/gene/1017'))
        res2 = self.msgpack_ok(self.get_ok(self.api + '/gene/1017?msgpack=true'))
        ok_(res, res2)

        res = self.json_ok(self.get_ok(self.api + '/query/?q=cdk'))
        res2 = self.msgpack_ok(self.get_ok(self.api + '/query/?q=cdk&msgpack=true'))
        ok_(res, res2)

        res = self.json_ok(self.get_ok(self.api + '/metadata'))
        res2 = self.msgpack_ok(self.get_ok(self.api + '/metadata?msgpack=true'))
        ok_(res, res2)


    def test_taxonomy(self):
        res = self.json_ok(self.get_ok(self.api + '/species/1239'))
        ok_("lineage" in res)

        res = self.json_ok(self.get_ok(self.api + '/species/46170?include_children=true'))
        ok_(len(res['children']) >= 305)

        res2 = self.json_ok(self.get_ok(self.api + '/species/46170?include_children=true&has_gene=1'))
        ok_(len(res2['children']) >= 16)
        ok_(len(res2['children']) <= len(res['children']))

        res = self.json_ok(self.get_ok(self.api + '/query?q=lytic%20enzyme&species=1386&include_tax_tree=true'))
        ok_(res['total'] >= 2)
        res2 = self.json_ok(self.get_ok(self.api + '/query?q=lytic%20enzyme&species=1386'))
        eq_(res2['total'], 0)


    def test_static(self):
        self.get_ok(self.host + '/favicon.ico')
        self.get_ok(self.host + '/robots.txt')


    def test_fetch_all(self):
        res = self.json_ok(self.get_ok(self.api + '/query?q=cdk2&fetch_all=true'))
        assert '_scroll_id' in res

        res2 = self.json_ok(self.get_ok(self.api + '/query?scroll_id=' + res['_scroll_id']))
        assert 'hits' in res2
        ok_(len(res2['hits']) >= 2)

    def test_dotfield(self):
        # /query service
        resdefault = self.json_ok(self.get_ok(self.api + '/query?q=cdk&fields=refseq.rna')) # default dotfield=0
        resfalse = self.json_ok(self.get_ok(self.api + '/query?q=cdk&fields=refseq.rna&dotfield=false')) # force no dotfield
        restrue = self.json_ok(self.get_ok(self.api + '/query?q=cdk&fields=refseq.rna&dotfield=true')) # force dotfield
        # check defaults and bool params
        eq_(resdefault["hits"],resfalse["hits"])
        # check struct
        assert "refseq.rna" in restrue["hits"][0].keys()
        assert "refseq" in resdefault["hits"][0].keys()
        assert "rna" in resdefault["hits"][0]["refseq"].keys()
        # TODO: no fields but dotfield => dotfield results
        # TODO: fields with dot but no dotfield => dotfield results

        # /gene service
        resdefault = self.json_ok(self.get_ok(self.api + '/gene/1017?filter=symbol,go.MF'))
        restrue = self.json_ok(self.get_ok(self.api + '/gene/1017?filter=symbol,go.MF&dotfield=true'))
        resfalse = self.json_ok(self.get_ok(self.api + '/gene/1017?filter=symbol,go.MF&dotfield=false'))
        eq_(resdefault,resfalse)
        assert "go.MF" in restrue.keys()
        assert "go" in resdefault.keys()
        assert "MF" in resdefault["go"].keys()

    def test_raw(self):
        # /gene
        raw1 = self.json_ok(self.get_ok(self.api + '/gene/1017?raw=1'))
        rawtrue = self.json_ok(self.get_ok(self.api + '/gene/1017?raw=true'))
        raw0  = self.json_ok(self.get_ok(self.api + '/gene/1017?raw=0'))
        rawfalse  = self.json_ok(self.get_ok(self.api + '/gene/1017?raw=false'))
        eq_(raw1,rawtrue)
        eq_(raw0,rawfalse)
        assert "_index" in raw1
        assert not "_index" in raw0
        assert "_source" in raw1
        assert not "_source" in raw0
        # /query
        raw1 = self.json_ok(self.get_ok(self.api + '/query?q=cdk&raw=1'))
        rawtrue = self.json_ok(self.get_ok(self.api + '/query?q=cdk&raw=true'))
        raw0  = self.json_ok(self.get_ok(self.api + '/query?q=cdk&raw=0'))
        rawfalse  = self.json_ok(self.get_ok(self.api + '/query?q=cdk&raw=false'))
        # this may vary so remove in comparison
        for d in [raw1,rawtrue,raw0,rawfalse]:
            del d["took"]
        eq_(raw1,rawtrue)
        eq_(raw0,rawfalse)
        assert "_shards" in raw1
        assert not "_shards" in raw0

    def test_species(self):
        res, con = self.h.request(self.api + "/species/9606")
        eq_(res.status, 200)
        eq_(res["content-location"],'http://s.biothings.io/v1/species/9606?include_children=1')
        d = _d(con.decode('utf-8'))
        eq_(set(d.keys()),set(['taxid', 'authority', 'lineage', '_id', 'common_name', 'genbank_common_name', '_version',
            'parent_taxid', 'scientific_name', 'has_gene', 'children', 'rank', 'uniprot_name']))


