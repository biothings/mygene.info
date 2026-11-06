from unittest import mock

import pytest

from biothings.tests.web import BiothingsWebAppTest
from biothings.web.query import AsyncESQueryPipeline, QueryPipelineException


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
        # AK3 is human AK4's former symbol: the genes now named AK3 in the
        # common species (human, mouse, rat, zebrafish) come first, then
        # human AK4, then the chicken AK3
        res = self.query(
            hits=True,
            q='AK3'
        )
        assert [hit['_id'] for hit in res['hits'][:6]] == ['50808', '56248', '26956', '406404', '205', '426534']

    def test_006_post_symbol_scope(self):
        # POST lookups rank like test_004 and test_005: the symbol scope also
        # searches prev_symbol, and adding alias doesn't change the order
        for scopes in ('symbol', 'symbol,alias'):
            res = self.request('query', method='POST', data={'q': 'PARK2,AK3', 'scopes': scopes}).json()
            ids = {term: [hit['_id'] for hit in res if hit['query'] == term] for term in ('PARK2', 'AK3')}
            assert ids['PARK2'] == ['5071', '421577'], scopes
            assert ids['AK3'] == ['50808', '56248', '26956', '406404', '205', '426534'], scopes

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
    """
    MygeneQueryPipeline (web.pipeline.batch) looks up a batch of IDs with one search.
    run_batch runs each batch through it and through AsyncESQueryPipeline, which searches
    each ID separately, and asserts that both return the same hits.

    The fixture has the real CDK2 (1017) and mouse Cdk2 (12566), plus made-up genes for
    the cases one search could get wrong:
    - 100000001 lists CDK2's ID 1017 as retired, so the term 1017 matches CDK2 by entrezgene
      and 100000001 by retired. Both are human and 100000001 is indexed first, so only the
      field boosts in batch.py rank CDK2 first, as BM25 does in the search per ID.
    - 2001-2006 share ENSG00000999999, in species with different weights. 2003's name has
      "pseudogene", which gets the lowest weight.
    - 3001 is another pseudogene, the hit test_query_full_window cuts off.
    """

    TEST_DATA_DIR_NAME = 'BatchLookupTests'
    SCOPES = ['_id', 'entrezgene', 'ensembl.gene', 'retired']
    IDS = [
        '1017', '1017', 100000001,  # Entrez IDs: CDK2 twice, and 100000001 as a JSON int
        'ENSG00000123374', 'ensg00000123374', 'ENSG00000123374.5',  # CDK2's Ensembl ID, lowercase, versioned
        '12566', 'ENSMUSG00000100000',  # mouse Cdk2, by Entrez ID and by its second Ensembl ID
        'ENSG00000999999',  # genes 2001-2006
        '999999',  # 100000001, by retired only
        'ENSDARG00000000001',  # a gene with only an Ensembl ID, which is its _id
        'nope', 'Cdk2',  # not found: junk, and a symbol
    ]

    def run_batch(self, method, ids, **options):
        """
        Run a batch through MygeneQueryPipeline and through AsyncESQueryPipeline, check that
        both return the same hits, and return the result and the searches the batch sent:
        ['Search'] for one search, ['MultiSearch'] for a search per ID, or ['Search',
        'MultiSearch'] when the hits didn't fit in one search.
        """
        pipeline = self._app.biothings.pipeline
        assert type(pipeline).__name__ == 'MygeneQueryPipeline'
        per_term = AsyncESQueryPipeline(pipeline.builder, pipeline.backend, pipeline.formatter, **pipeline.settings)
        with mock.patch.object(pipeline.backend, 'execute', wraps=pipeline.backend.execute) as execute:
            result = self.io_loop.run_sync(lambda: getattr(pipeline, method)(ids, **options))
        expected = self.io_loop.run_sync(lambda: getattr(per_term, method)(ids, **options))

        def without_scores(res):
            if isinstance(res, dict):  # with_total
                return {**res, 'hits': without_scores(res['hits'])}
            return [{key: value for key, value in hit.items() if key != '_score'} for hit in res]

        assert without_scores(result) == without_scores(expected)
        return result, [type(call.args[0]).__name__ for call in execute.call_args_list]

    @staticmethod
    def hits_of(result, q):
        return [hit['_id'] for hit in result if hit['query'] == q and not hit.get('notfound')]

    def test_query(self):
        result, searches = self.run_batch('search', self.IDS, scopes=self.SCOPES, species=['all'])
        assert searches == ['Search']
        # CDK2, whose current ID is 1017, ranks above 100000001, which retired it (1017 is in IDS twice)
        assert self.hits_of(result, '1017') == ['1017', '100000001'] * 2
        # _score is per term, so terms that share a hit get their own copy: 100000001
        # is a retired match for 1017 and an entrezgene match for 100000001
        score = {(hit['query'], hit['_id']): hit['_score'] for hit in result if '_id' in hit}
        assert score['1017', '1017'] > score['1017', '100000001']
        assert score['1017', '100000001'] < score[100000001, '100000001']
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
        # one search fetches at most 2 terms x size 2 = 4 hits. The 6 genes with ENSG00000999999
        # fill them and cut off 3001, so the batch runs again with a search per ID.
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

    def test_msearch_fallback(self):
        # batches one search can't answer the same way run with a search per ID, like
        # the symbol scope, which gets the fixed scores in legacy.py even next to ID fields
        result, searches = self.run_batch(
            'search', ['CDK2', 'Cdk2', '1017'], scopes=['entrezgene', 'symbol'], species=['all']
        )
        assert searches == ['MultiSearch']
        assert self.hits_of(result, 'CDK2') == ['1017', '12566']
        _, searches = self.run_batch('search', self.IDS, scopes=self.SCOPES, species=['all'], **{'from': 1})
        assert searches == ['MultiSearch']
        # retired is a long, Elasticsearch searches it for 1017 when the term is 1017.0
        result, searches = self.run_batch('search', ['1017.0', '1017'], scopes=self.SCOPES, species=['all'])
        assert searches == ['MultiSearch']
        assert self.hits_of(result, '1017.0') == ['100000001']

    def test_unusual_terms(self):
        # more digits than int() accepts: not found, as with a search per ID
        result, searches = self.run_batch('search', ['1' * 5000, '1017'], scopes=self.SCOPES, species=['all'])
        assert searches == ['Search']
        assert self.hits_of(result, '1' * 5000) == []
        # a search per ID rejects the term 0 as empty, and so does the batch
        with pytest.raises(QueryPipelineException) as raised:
            self.io_loop.run_sync(lambda: self._app.biothings.pipeline.search([0], scopes=self.SCOPES))
        assert raised.value.code == 400

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
