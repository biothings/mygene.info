import pytest

from biothings.tests.web import BiothingsWebAppTest


class TestAnnotationScopes(BiothingsWebAppTest):
    TEST_DATA_DIR_NAME = 'AnnotationTests'

    def test_id(self):
        q = '1017'
        res = self.request("gene", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert res[0]['_id'] == q

    def test_ensg(self):
        q = 'ENSG00000123374'
        res = self.request("gene", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result(q, res, 'ensembl.gene')

    def test_retired(self):
        q = '102938628'
        res = self.request("gene", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result(q, res, 'retired') or \
            self.value_in_result(int(q), res, 'retired')

    # cannot test for entrez != _id (no such data)
    # not adding a mock data for this case because this seems unlikely
    # to be screwed up


class TestQuery(BiothingsWebAppTest):
    TEST_DATA_DIR_NAME = 'QueryTests'

    def test_000_basic_query(self):
        self.query(
            hits=True,
            q='cdk2'
        )

    def test_001_query_string(self):
        q = "symbol:CDK2"
        res = self.query(
            hits=True,
            q=q
        )
        assert res['total'] == 1
        assert res['hits'][0]['symbol'] == 'CDK2'

    def test_002_wildcard(self):
        q = "cdk?"
        # if we have more data, maybe this test case needs fixing
        res = self.query(
            hits=True,
            q=q
        )
        for hit in res['hits']:
            assert hit['symbol'].lower().startswith('cdk')
            assert len(hit['symbol']) == 4

    def test_003_entrez_int(self):
        q = "1017"
        res = self.query(
            hits=True,
            q=q
        )
        for hit in res['hits']:
            assert self.value_in_result(int(q), hit, 'entrezgene') or \
                self.value_in_result(q, hit, 'entrezgene')

    def test_010_taxtree_true(self):
        self.query(
            hits=True,
            q='lytic enzyme', species='1385', include_tax_tree=True
        )

    def test_011_taxtree_false(self):
        self.query(
            hits=False,
            q='lytic enzyme', species='1385',
        )

    def test_012_species_translation(self):
        res = self.query(
            hits=True,
            q='__all__', species='human',
        )
        for hit in res['hits']:
            assert self.value_in_result(9606, hit, 'taxid') or \
                self.value_in_result("9606", hit, 'taxid')

    @pytest.mark.skip("this is also impossible to trigger. "
                      "It gets casted before reaching the pipeline")
    def test_013_species_type_error(self):
        self.request('query', method='POST', expect=400,
                     data={'q': '__all__', 'species': True})

    def test_014_species_translation_fail(self):
        self.request('query', params={
            'q': '__all__', 'species': 'elf',  # I don't see this test case changing soon
        }, expect=400)

    def test_020_interval_query_hg38(self):
        q = 'chr12:55,966,782-55,972,788'
        # should hit 1017
        self.query(
            hits=True,
            q=q,
        )

    def test_021_interval_query_hg19(self):
        q = 'hg19.chr12:56360553-56366568'
        # should hit 1017
        self.query(
            hits=True,
            q=q,
        )

    def test_022_interval_query_out_of_range(self):
        q = 'chr24:0-0'  # I don't think there's such thing
        # should hit 1017
        self.query(
            hits=False,
            q=q,
        )

    @pytest.mark.skip("not implemented")
    def test_023_bad_interval(self):
        # I wanted to test other branches of
        # web.pipeline.legacy but turns out it's more or less impossible
        # to reach
        q = 'chr1:,,,-,,,'
        self.request('query', expect=400, data={'q': q})

    def test_030_entrezonly(self):
        q = "__all__"
        res = self.query(
            hits=True,
            q=q, entrezonly=True
        )
        for hit in res['hits']:
            assert 'entrezgene' in hit

    def test_031_ensemblonly(self):
        q = "__all__"
        res = self.query(
            hits=True,
            q=q, ensemblonly=True
        )
        for hit in res['hits']:
            assert 'ensembl' not in hit or 'gene' not in hit['ensembl']

    def test_032_missing(self):
        q = "__all__"
        res = self.query(
            hits=True,
            q=q, missing='entrezgene'
        )
        for hit in res['hits']:
            assert 'entrezgene' not in hit

    def test_033_exists(self):
        q = "__all__"
        res = self.query(
            hits=True,
            q=q, exists='ensembl.gene', fields='ensembl.gene'
        )
        for hit in res['hits']:
            assert 'ensembl' in hit and 'gene' in hit['ensembl']

    def test_040_species_facet_filter(self):
        q = "__all__"
        taxid = 9606
        res1 = self.query(
            hits=True,
            q=q, aggs='type_of_gene', size=10
        )
        res2 = self.query(
            hits=True,
            q=q, aggs='type_of_gene', species=taxid, size=10
        )
        res3 = self.query(
            hits=True,
            q=q, aggs='type_of_gene', species_facet_filter=taxid,size=10
        )
        assert res1['facets'] != res2['facets']
        assert res1['facets'] == res3['facets']
        for hit in res3['hits']:
            assert hit['taxid'] == taxid


class TestMetadata(BiothingsWebAppTest):
    TEST_DATA_DIR_NAME = 'QueryTests'

    def test_metadata_extra(self):
        res = self.request('metadata')
        res = res.json()
        assert 'genome_assembly' in res
        assert isinstance(res['genome_assembly'], dict)
        assert 'taxonomy' in res
        assert isinstance(res['taxonomy'], dict)
