from unittest import mock

import pytest

from biothings.tests.web import BiothingsWebAppTest
from biothings.web.query import AsyncESQueryPipeline


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

    def test_004_prev_symbol(self):
        # human PRKN (formerly PARK2) outranks a chicken gene still named PARK2
        res = self.query(
            hits=True,
            q='PARK2'
        )
        assert res['hits'][0]['_id'] == '5071'
        assert res['hits'][1]['_id'] == '421577'

    def test_005_symbol_above_prev_symbol(self):
        # AK3 is human AK4's former symbol, but the genes now named AK3 in
        # human and mouse come first
        res = self.query(
            hits=True,
            q='AK3'
        )
        assert [hit['_id'] for hit in res['hits'][:3]] == ['50808', '56248', '205']

    def test_010_taxtree_true(self):
        self.query(
            hits=True,
            q='spore cortex-lytic enzyme', species='189381', include_tax_tree=True,
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


class TestBatchLookup(BiothingsWebAppTest):
    # web.pipeline.batch: one search for a batch of IDs. Some fixture genes are made up:
    # 100000001 lists the live ID 1017 as retired, 2001-2006 share one Ensembl ID.
    TEST_DATA_DIR_NAME = 'BatchLookupTests'
    SCOPES = ['_id', 'entrezgene', 'ensembl.gene', 'retired']
    IDS = [
        '1017', 'ENSG00000123374', 'ensg00000123374', '12566', 'ENSMUSG00000100000', 'ENSG00000999999',
        '999999', 'ENSDARG00000000001', '1017', 'nope', 'ENSG00000123374.5', 'Cdk2', 100000001,
    ]

    def run_batch(self, method, ids, **options):
        """
        Run a batch through MygeneQueryPipeline and through AsyncESQueryPipeline,
        which searches each term, check that both return the same hits, and
        return the result and the class names of the searches the batch ran.
        """
        pipeline = self._app.biothings.pipeline
        assert type(pipeline).__name__ == 'MygeneQueryPipeline'
        per_term = AsyncESQueryPipeline(pipeline.builder, pipeline.backend, pipeline.formatter, **pipeline.settings)
        with mock.patch.object(pipeline.backend, 'execute', wraps=pipeline.backend.execute) as execute:
            result = self.io_loop.run_sync(lambda: getattr(pipeline, method)(ids, **options))
        expected = self.io_loop.run_sync(lambda: getattr(per_term, method)(ids, **options))

        def without_scores(res):
            hits = res['hits'] if isinstance(res, dict) else res
            return [{key: value for key, value in hit.items() if key != '_score'} for hit in hits]

        assert without_scores(result) == without_scores(expected)
        if isinstance(result, dict):  # with_total
            assert {**result, 'hits': None} == {**expected, 'hits': None}
        return result, [type(call.args[0]).__name__ for call in execute.call_args_list]

    @staticmethod
    def hits_of(result, q):
        return [hit['_id'] for hit in result if hit['query'] == q and not hit.get('notfound')]

    def test_query(self):
        result, searches = self.run_batch('search', self.IDS, scopes=self.SCOPES, species=['all'])
        assert searches == ['Search']
        # the gene whose current ID is 1017 ranks above the gene that retired it,
        # for both times 1017 is in IDS
        assert self.hits_of(result, '1017') == ['1017', '100000001'] * 2
        scores = [hit['_score'] for hit in result if hit['query'] == '1017']
        assert scores[0] > scores[1]
        # human, rat, zebrafish, then chimpanzee (a tie, kept in index order), and the pseudogene last
        assert self.hits_of(result, 'ENSG00000999999') == ['2001', '2002', '2004', '2005', '2006', '2003']
        assert self.hits_of(result, 'ensg00000123374') == ['1017']
        assert self.hits_of(result, 100000001) == ['100000001']
        assert self.hits_of(result, 'ENSG00000123374.5') == []

    def test_query_species_size_with_total(self):
        result, searches = self.run_batch(
            'search', self.IDS, scopes=self.SCOPES, species=['9606', '10090'], size=2, with_total=True
        )
        assert searches == ['Search']
        assert self.hits_of(result['hits'], 'ENSG00000999999') == ['2001', '2003']
        result, searches = self.run_batch(
            'search', self.IDS, scopes=self.SCOPES, species=['all'], size=2, with_total=True
        )
        assert searches == ['Search']
        assert self.hits_of(result['hits'], 'ENSG00000999999') == ['2001', '2002']
        assert result['max_total'] == 6

    def test_query_full_window(self):
        # with size=2, one search returns 4 hits for 2 terms, and the 6 genes that list
        # ENSG00000999999 push out pseudogene 3001, the only hit of the other term
        result, searches = self.run_batch(
            'search', ['ENSG00000999999', '3001'], scopes=self.SCOPES, species=['all'], size=2
        )
        assert searches == ['Search', 'MultiSearch']
        assert self.hits_of(result, 'ENSG00000999999') == ['2001', '2002']
        assert self.hits_of(result, '3001') == ['3001']

    def test_gene(self):
        ids = [
            '1017', 'NCBIGene:1017', 'ENSEMBL:ENSG00000999999', 'ENSG00000123374', '999999', '12566', 'nope',
            'ENSDARG00000000001',
        ]
        result, searches = self.run_batch('fetch', ids, species=['all'])
        assert searches == ['Search']
        assert self.hits_of(result, 'NCBIGene:1017') == ['1017', '100000001']
        assert len(self.hits_of(result, 'ENSEMBL:ENSG00000999999')) == 6

    def test_searches_each_term(self):
        _, searches = self.run_batch('search', ['CDK2', 'Cdk2'], scopes=['symbol'], species=['all'])
        assert searches == ['MultiSearch']
        _, searches = self.run_batch('search', self.IDS, scopes=self.SCOPES, species=['all'], **{'from': 1})
        assert searches == ['MultiSearch']
        # retired is a long, Elasticsearch searches it for 1017 when the term is 1017.0
        result, searches = self.run_batch('search', ['1017.0', '1017'], scopes=self.SCOPES, species=['all'])
        assert searches == ['MultiSearch']
        assert self.hits_of(result, '1017.0') == ['100000001']

    def test_post_endpoints(self):
        res = self.request('query', method='POST', data={
            'q': '1017,ENSG00000999999', 'scopes': 'entrezgene,ensembl.gene,retired', 'species': 'human',
        }).json()
        assert [(hit['query'], hit['_id']) for hit in res] == [
            ('1017', '1017'), ('1017', '100000001'), ('ENSG00000999999', '2001'), ('ENSG00000999999', '2003'),
        ]
        res = self.request('gene', method='POST', data={'ids': '1017,ENSDARG00000000001,nope'}).json()
        assert [(hit['query'], hit.get('_id'), hit.get('notfound')) for hit in res] == [
            ('1017', '1017', None), ('1017', '100000001', None),
            ('ENSDARG00000000001', 'ENSDARG00000000001', None), ('nope', None, True),
        ]


class TestMetadata(BiothingsWebAppTest):
    TEST_DATA_DIR_NAME = 'QueryTests'

    def test_metadata_extra(self):
        res = self.request('metadata')
        res = res.json()
        assert 'genome_assembly' in res
        assert isinstance(res['genome_assembly'], dict)
        assert 'taxonomy' in res
        assert isinstance(res['taxonomy'], dict)
