from biothings.tests.web import BiothingsDataTest


class TestSpecialInput(BiothingsDataTest):
    host = 'mygene.info'
    prefix = 'v3'

    unicode_text = u'基因'

    def test_400_unicode(self):
        self.request('gene/' + self.unicode_text, expect=404)

    def test_401_unicode(self):
        res = self.request("gene", method='POST', data={'ids': self.unicode_text}).json()
        assert res[0]['notfound']
        assert len(res) == 1

    def test_402_unicode(self):
        res = self.request("gene", method='POST', data={'ids': '1017, ' + self.unicode_text}).json()
        assert res[1]['notfound']
        assert len(res) == 2

    def test_403_unicode(self):
        res = self.query(q=self.unicode_text, hits=False)
        assert res['hits'] == []

    def test_404_unicode(self):
        res = self.query(method='POST', q=self.unicode_text, scopes='symbol', hits=False)
        assert res[0]['notfound']
        assert len(res) == 1

    def test_405_unicode(self):
        res = self.query(method='POST', q='cdk2+' + self.unicode_text, hits=False)
        assert res[1]['notfound']
        assert len(res) == 2

    def test_411_case_sensitivity(self):
        # case-insensitive sources
        self.query(q='mirbase:MI0017267')

    def test_412_case_sensitivity(self):
        self.query(q='wormbase:WBGene00019362', species=6239)

    def test_413_case_sensitivity(self):
        self.query(q='xenbase:XB-GENE-1001990', species='frog')

    def test_414_case_sensitivity(self):
        self.query(q='Xenbase:XB-GENE-1001990', species='frog')

    def test_415_case_sensitivity(self):
        self.query(q=r'MGI:MGI\:104772')

    def test_416_case_sensitivity(self):
        self.query(q=r'mgi:MGI\:104772')

    def test_417_case_sensitivity(self):
        # sometimes the orders of results are *slightly* different for cdk2 and CDK2
        # so limit to top 3 more stable results
        lower = filter_hits(self.request("query?q=cdk2&size=3").json())
        upper = filter_hits(self.request("query?q=CDK2&size=3").json())
        assert lower["hits"] == upper["hits"]

    def test_421_species_order(self):
        res = self.request("query?q=cdk2&species=human,mouse,rat").json()
        hits = res["hits"]
        # first is 1017, it's human and cdk2 is a symbol
        assert hits[0]["_id"] == "1017"
        # second is 12566, mouse
        assert hits[1]["_id"] == "12566"
        # third is 362817, rat
        assert hits[2]["_id"] == "362817"

    def test_422_value_type(self):

        res = self.request("gene/1017?species=9606&fields=homologene,exons").json()
        check_homologene(res)
        check_exons(res)

    def test_423_value_type(self):
        resall = self.request("gene/1017?fields=homologene,exons").json()
        check_homologene(resall)
        check_exons(resall)


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

def check_homologene(res):
    for item in res["homologene"]["genes"]:
        assert isinstance(item[0], int)
        assert isinstance(item[1], int)

def check_exons(res):
    for ex in res["exons"]:
        for pos in ex["position"]:
            assert isinstance(pos[0], int)
            assert isinstance(pos[1], int)