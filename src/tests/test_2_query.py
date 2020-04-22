import random


from biothings.tests.web import BiothingsTestCase


class TestQueryGET(BiothingsTestCase):

    def test_201_query(self):
        # data existance
        self.query(q='cdk2')
        self.query(q='GO:0004693')
        self.query(q='reporter:211803_at')
        self.query(q='IPR008351')
        self.query(q='hsa-mir-503')
        self.query(q='hsa-miR-503')

    def test_202_query(self):
        # fielded query
        self.query(q='symbol:cdk2')

    def test_203_query(self):
        # interval query
        self.query(q='chr1:151,073,054-151,383,976&species=human')

    def test_204_query(self):
        pass # feature removed in biothings 0.7.0
        # con = self.request('query?q=cdk2&callback=mycallback').content
        # assert con.startswith(b'mycallback(')

    def test_205_query(self):
        # non-ascii character
        res = self.query(q='54097\xef\xbf\xbd\xef\xbf\xbdmouse', hits=False)
        assert res['hits'] == []

    def test_206_query(self):
        self.request('query', expect=400)

    def test_207_query(self):
        self.request('query?q=tRNA:Y1:85Ae', expect=400)

    def test_208_query(self):
        # default returned fields
        res = self.request('query?q=cdk').json()
        deffields = res["hits"][0].keys()
        expected = ["_id", "_score", "taxid", "entrezgene", "name", "symbol"]
        assert sorted(list(deffields)) == sorted(expected)

    def test_209_query(self):
        # entrezonly for match query
        query_data = {
            "q": "FAM86B3P",
            "scopes": "symbol, alias",
            "entrezonly": "True"
        }
        res = self.query(method='POST', data=query_data)
        assert len(res) == 1
        del query_data["entrezonly"]
        res = self.query(method='POST', data=query_data)
        assert len(res) == 3

    def test_210_size(self):
        res = self.request('query?q=cdk?').json()
        assert len(res['hits']) == 10  # default is 10
        assert res['total'] > 10

    def test_211_size(self):
        res = self.request('query?q=cdk?&size=0').json()
        assert len(res['hits']) == 0

    def test_212_size(self):
        res = self.request('query?q=cdk?&limit=20').json()
        assert len(res['hits']) == 20

    def test_213_size(self):
        res1 = self.request("query?q=cdk?&from=0&size=20").json()
        res = self.request("query?q=cdk?&skip=10&size=20").json()
        assert len(res['hits']) == 20
        assert res['hits'][0] in res1['hits']

    def test_214_size(self):
        # API doc says cap 1000
        res = self.request('query?q=*&size=1000').json()
        assert len(res['hits']) == 1000

    def test_215_size(self):
        res = self.request('query?q=*&size=1001', expect=400)
        res = self.request('query?q=*&size=2000', expect=400)

    def test_216_size(self):
        self.request('query?q=cdk?&size=1a', expect=400)

    def test_221_facet(self):
        res = self.request('query?q=cdk?&facets=taxid&species=human,mouse,rat').json()
        assert 'facets' in res
        assert 'taxid' in res['facets']
        assert res['facets']['taxid']['total'] == res['total']
        assert res['facets']['taxid']['other'] == 0
        assert res['facets']['taxid']['missing'] == 0

    def test_222_facet(self):
        res_t = self.request(
            "query?q=symbol:cdk?&facets=type_of_gene&species=human,mouse,rat").json()
        assert 'facets' in res_t
        assert 'type_of_gene' in res_t['facets']
        assert "term" in res_t['facets']['type_of_gene']['terms'][0]
        assert res_t['facets']['type_of_gene']['terms'][0]['term'] == 'protein-coding'

    def test_223_facet(self):
        res = self.request('query?q=cdk?&facets=taxid&species=human,mouse,rat').json()
        url = 'query?q=cdk?&facets=taxid&species_facet_filter=human&species=human,mouse,rat'
        res2 = self.request(url).json()
        assert res2['facets']['taxid']['total'] == res['total']
        assert res2['facets']['taxid'] == res['facets']['taxid']
        assert [x["count"] for x in res2['facets']['taxid']['terms'] if x["term"] == 9606][0] == res2['total']

    def test_231_sort(self):
        res = self.request("query?q=MTFMT&sort=taxid&species=human,mouse,rat").json()
        hits = res["hits"]
        assert len(hits) == 3
        assert hits[0]["entrezgene"] == "123263"
        assert hits[1]["entrezgene"] == "69606"
        assert hits[2]["entrezgene"] == "315763"

    def test_241_userquery(self):

        res1 = self.request('query?q=cdk').json()
        res2 = self.request("query?q=cdk&userquery=bgood_cure_griffith").json()
        assert res1['total'] > res2['total']

    def test_242_userquery(self):
        # nonexisting user filter gets ignored
        res1 = self.request('query?q=cdk').json()
        res2 = self.request("query?q=cdk&userquery=aaaa").json()
        assert res1['total'] == res2['total']

    def test_251_exists(self):
        res1 = self.request('query?q=cdk').json()
        res2 = self.request("query?q=cdk&exists=pharmgkb").json()
        assert res1['total'] > res2['total']
        res3 = self.request("query?q=cdk&exists=pharmgkb,pdb").json()
        assert res2['total'] > res3['total']

    def test_252_missing(self):

        res1 = self.request('query?q=cdk').json()
        res2 = self.request('query?q=cdk&missing=pdb').json()
        assert res1['total'] > res2['total']
        res3 = self.request("query?q=cdk&missing=pdb,MIM").json()
        assert res2['total'] > res3['total']

    def test_253_interval(self):

        self.query(q='chr1:1000-100000', species='human')

    def test_254_fetch_all(self):

        res = self.request("query?q=cdk*&species=all&fetch_all=true").json()
        assert '_scroll_id' in res

        res2 = self.query(scroll_id=res['_scroll_id'])
        assert 'hits' in res2
        assert len(res2['hits']) >= 2

    def test_255_taxtree(self):

        url = 'query?q=lytic%20enzyme&species=1386&include_tax_tree=true'
        res = self.request(url).json()
        assert res['total'] >= 2
        res2 = self.request("query?q=lytic%20enzyme&species=1386").json()
        assert res2['total'] == 0


class TestQueryPOST(BiothingsTestCase):

    def test_261_post(self):

        data = {'q': '1017', 'scopes': 'entrezgene'}
        res = self.request('query', method='POST', data=data).json()
        assert len(res) == 1
        assert set(res[0].keys()) == set(['query', 'taxid', '_score', 'entrezgene', 'symbol', '_id', 'name'])
        assert res[0]['_id'] == '1017'

    def test_262_post(self):

        data = {'q': '211803_at,1018', 'scopes': 'reporter,entrezgene'}
        res = self.request('query', method='POST', data=data).json()
        assert len(res) == 2
        assert res[0]['_id'] == '1017'
        assert res[1]['_id'] == '1018'

    def test_263_post(self):

        data = {'q': 'CDK2',
                'species': 'human,10090,frog,pig',
                'scopes': 'symbol',
                'fields': 'name,symbol'}
        res = self.request('query', method='POST', data=data).json()
        assert len(res) >= 4, (res, len(res))
        self.request('query', expect=400)

    def test_264_post(self):

        data = {'q': '[1017, "1018"]',
                'scopes': 'entrezgene',
                'jsoninput': 'true'}
        res = self.request('query', method='POST', data=data).json()
        assert len(res) == 2
        assert res[0]['_id'] == '1017'
        assert res[1]['_id'] == '1018'

    def test_265_post(self):

        body = {
            'q': '"cyclin dependent kinase 2", "cyclin dependent kinase 3"',
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
