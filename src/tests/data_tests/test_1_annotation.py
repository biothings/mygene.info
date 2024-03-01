import pytest
import requests

from biothings.tests.web import BiothingsDataTest


class TestAnnotationGET(BiothingsDataTest):
    host = "localhost:8000"
    prefix = "v3"

    def test_101(self):
        res = self.request("gene/1017").json()

        attr_li = [
            "HGNC",
            "MIM",
            "_id",
            "accession",
            "alias",
            "ec",
            "ensembl",
            "entrezgene",
            "genomic_pos",
            "go",
            "homologene",
            "interpro",
            "ipi",
            "map_location",
            "name",
            "pir",
            "pdb",
            "pharmgkb",
            "prosite",
            "reagent",
            "refseq",
            "reporter",
            "summary",
            "symbol",
            "taxid",
            "type_of_gene",
            "unigene",
            "uniprot",
            "exons",
            "generif",
        ]
        # Removed 'Vega' as an attribute in tests 2019/3

        for attr in attr_li:
            assert attr in res

        res = self.request("gene/12566").json()
        attr_li = [
            "MGI",
            "_id",
            "accession",
            "alias",
            "ec",
            "ensembl",
            "entrezgene",
            "genomic_pos",
            "go",
            "homologene",
            "interpro",
            "ipi",
            "map_location",
            "name",
            "prosite",
            "reagent",
            "refseq",
            "reporter",
            "symbol",
            "taxid",
            "type_of_gene",
            "unigene",
            "uniprot",
            "exons",
            "generif",
        ]

        for attr in attr_li:
            assert attr in res

        res = self.request("gene/245962").json()
        attr_li = [
            "RGD",
            "_id",
            "accession",
            "alias",
            "ensembl",
            "entrezgene",
            "genomic_pos",
            "go",
            "homologene",
            "interpro",
            "ipi",
            "map_location",
            "name",
            "prosite",
            "refseq",
            "reporter",
            "symbol",
            "taxid",
            "type_of_gene",
            "unigene",
            "uniprot",
            "exons",
            "generif",
        ]

        for attr in attr_li:
            assert attr in res

    def test_102(self):
        pairs = [
            (12566, "MGI"),
            (245962, "RGD"),
            (493498, "Xenbase"),
            (406715, "ZFIN"),
            (824036, "TAIR"),
            (42453, "FLYBASE"),
        ]

        for _id, attr in pairs:
            res = self.request("gene/" + str(_id)).json()
            assert attr in res

    def test_103(self):
        # pig
        res = self.request("gene/397593").json()
        assert "reporter" in res
        assert "snowball" in res["reporter"]

    def test_104(self):
        # nematode
        self.request("gene/172677").json()

    def test_105(self):
        # this is not nematode, "taxid": 31234
        res = self.request("gene/171911").json()
        assert "WormBase" in res

    def test_106(self):
        # fission yeast
        self.request("gene/2539869").json()

    def test_107(self):
        # e coli.
        # res = self.request('gene/12931566').json()
        pass

    def test_108(self):
        # mirna
        res = self.request("gene/406881").json()
        assert "miRBase" in res

    def test_109(self):
        res = self.request("gene/1017").json()
        assert res["entrezgene"] == "1017"

    def test_110(self):
        # testing non-ascii character
        self.request("gene/54097\xef\xbf\xbd\xef\xbf\xbdmouse", expect=404)

    def test_111(self):
        # one test to /gene/Y105C5B.255 has been removed
        # since dots in geneids are no longer supported
        pass

    def test_112(self):
        """GET /v3/gene/
        {
            "code": 400,
            "success": false,
            "error": "Bad Request",
            "missing": "id"
        }
        """
        self.request("gene", expect=400)

    def test_113(self):
        self.request("gene/", expect=400)

    # @pytest.mark.xfail(
    #     reason="CURIE ID SUPPORT NOT CURRENTLY ENABLED ON MYGENE.INFO HOST",
    #     run=True,
    #     strict=True,
    # )
    def test_114(self):
        """
        Tests the annotation endpoint support for the biolink CURIE ID.

        If support is enabled then we should retrieve the exact same document
        for all the provided queries

        A mirror copy of the tests we have in the biothings_client
        package (gene.py)
        """
        curie_id_testing_collection = [
            ("1017", "entrezgene:1017", "NCBIgene:1017"),
            (1017, "entrezgene:1017", "ncbigene:1017"),
            ("1017", "entrezgene:1017", "NCBIGENE:1017"),
            ("1018", "ensembl.gene:ENSG00000250506", "ENSEMBL:ENSG00000250506"),
            (1018, "ensembl.gene:ENSG00000250506", "ensembl:ENSG00000250506"),
            (
                "ENSG00000250506",
                "ensembl.gene:ENSG00000250506",
                "ENSEMBL:ENSG00000250506",
            ),
            (
                "ensg00000250506",
                "ensembl.gene:ENSG00000250506",
                "ENSEMBL:ENSG00000250506",
            ),
            ("5995", "uniprot.Swiss-Prot:P47804", "UniProtKB:P47804"),
            (5995, "uniprot.Swiss-Prot:P47804", "UNIPROTKB:P47804"),
            ("5995", "uniprot.Swiss-Prot:P47804", "uniprotkb:P47804"),
        ]

        results_aggregation = []
        endpoint = "gene"
        for id_query, biothings_query, biolink_query in curie_id_testing_collection:
            id_query_result = self.request(f"{endpoint}/{id_query}", expect=200)
            assert isinstance(id_query_result, requests.models.Response)
            assert id_query_result.url == self.get_url(path=f"{endpoint}/{id_query}")

            biothings_term_query_result = self.request(
                f"{endpoint}/{biothings_query}", expect=200
            )
            assert isinstance(biothings_term_query_result, requests.models.Response)
            assert biothings_term_query_result.url == self.get_url(
                path=f"{endpoint}/{biothings_query}"
            )

            biolink_term_query_result = self.request(
                f"{endpoint}/{biolink_query}", expect=200
            )
            assert isinstance(biolink_term_query_result, requests.models.Response)
            assert biolink_term_query_result.url == self.get_url(
                path=f"{endpoint}/{biolink_query}"
            )

            results_aggregation.append(
                (
                    id_query_result.json() == biothings_term_query_result.json(),
                    id_query_result.json() == biolink_term_query_result.json(),
                    biothings_term_query_result.json()
                    == biolink_term_query_result.json(),
                )
            )

        results_validation = []
        failure_messages = []
        for result, test_query in zip(results_aggregation, curie_id_testing_collection):
            cumulative_result = all(result)
            if not cumulative_result:
                failure_messages.append(
                    f"Query Failure: {test_query} | Results: {result}"
                )
            results_validation.append(cumulative_result)

        assert all(results_validation), "\n".join(failure_messages)

    def test_115(self):
        """
        Tests the annotation endpoint support for the biolink CURIE ID.

        Invalid query evaluating we still return properly return a missing document result
        """
        invalid_query = "tree:293484"
        expected_invalid_status_code = 404
        endpoint = "gene"
        invalid_query_result = self.request(
            f"{endpoint}/{invalid_query}", expect=expected_invalid_status_code
        )
        assert isinstance(invalid_query_result, requests.models.Response)
        assert invalid_query_result.url == self.get_url(
            path=f"{endpoint}/{invalid_query}"
        )

        expected_json_response = {"code": 404, "success": False, "error": "Not Found."}
        assert invalid_query_result.json() == expected_json_response


class TestAnnotationPOST(BiothingsDataTest):
    host = "localhost:8000"
    prefix = "v3"

    def test_151(self):
        res = self.request("gene", method="POST", data={"ids": "1017"}).json()
        assert len(res) == 1
        assert res[0]["entrezgene"] == "1017"

        # check default fields returned
        default_fields = [
            "symbol",
            "reporter",
            "refseq",
            "pdb",
            "interpro",
            "entrezgene",
            "summary",
            "genomic_pos_hg19",
            "unigene",
            "ipi",
            "taxid",
            "pfam",
            "homologene",
            "ensembl",
            "ec",
            "type_of_gene",
            "pathway",
            "exons_hg19",
            "MIM",
            "generif",
            "HGNC",
            "name",
            "reagent",
            "uniprot",
            "pharmgkb",
            "alias",
            "genomic_pos",
            "accession",
            "_id",
            "pir",
            "prosite",
            "wikipedia",
            "go",
            "query",
            "map_location",
            "exons",
            "exac",
            "other_names",
            "umls",
            "pantherdb",
            "pharos",
            "_version",
        ]

        for field in default_fields:
            assert field in res[0]
        assert len(default_fields) <= len(res[0])

    def test_152(self):
        res = self.request("gene", method="POST", data={"ids": "1017, 1018"}).json()
        assert len(res) == 2
        assert res[0]["_id"] == "1017"
        assert res[1]["_id"] == "1018"

    def test_153(self):
        data = {"ids": "1017,1018", "fields": "symbol,name,entrezgene"}
        res = self.request("gene", method="POST", data=data).json()
        assert len(res) == 2
        for _g in res:
            assert set(_g) == set(
                ["_id", "_version", "query", "symbol", "name", "entrezgene"]
            )

    def test_154(self):
        data = {"ids": "1017,1018", "fields": "symbol,go.MF"}
        res = self.request("gene", method="POST", data=data).json()
        assert len(res) == 2
        for _g in res:
            assert set(_g) == set(["_id", "_version", "query", "symbol", "go"])
            assert "MF" in _g["go"]

    def test_155(self):
        # get retired gene
        res = self.request("gene", method="POST", data={"ids": "791256"}).json()
        assert res[0]["_id"] == "50846"  # this is the corresponding _id field

    @pytest.mark.xfail(
        reason="CURIE ID SUPPORT NOT CURRENTLY ENABLED ON MYGENE.INFO HOST",
        run=True,
        strict=True,
    )
    def test_156(self):
        """
        Tests the annotations endpoint support for the biolink CURIE ID.

        Batch query testing against the POST endpoint to verify that the CURIE ID can work with
        multiple

        If support is enabled then we should retrieve the exact same document for all the provided
        queries

        A mirror copy of the tests we have in the biothings_client
        package (gene.py)
        """
        curie_id_testing_collection = [
            ("1017", "entrezgene:1017", "NCBIgene:1017"),
            (1017, "entrezgene:1017", "ncbigene:1017"),
            ("1017", "entrezgene:1017", "NCBIGENE:1017"),
            ("1018", "ensembl.gene:ENSG00000250506", "ENSEMBL:ENSG00000250506"),
            (1018, "ensembl.gene:ENSG00000250506", "ensembl:ENSG00000250506"),
            ("5995", "uniprot.Swiss-Prot:P47804", "UniProtKB:P47804"),
            (5995, "uniprot.Swiss-Prot:P47804", "UNIPROTKB:P47804"),
            ("5995", "uniprot.Swiss-Prot:P47804", "uniprotkb:P47804"),
        ]

        results_aggregation = []
        endpoint = "gene"
        for id_query, biothings_query, biolink_query in curie_id_testing_collection:
            base_result = self.request(f"{endpoint}/{id_query}", expect=200)

            query_collection = (id_query, biothings_query, biolink_query)
            delimiter = ","
            data_mapping = {
                "ids": delimiter.join([f'"{query}"' for query in query_collection])
            }
            query_results = self.request(
                endpoint, method="POST", data=data_mapping
            ).json()
            assert len(query_results) == len(query_collection)

            batch_id_query = query_results[0]
            batch_biothings_query = query_results[1]
            batch_biolink_query = query_results[2]

            batch_id_query_return_value = batch_id_query.pop("query")
            assert batch_id_query_return_value == str(id_query)

            batch_biothings_query_return_value = batch_biothings_query.pop("query")
            assert batch_biothings_query_return_value == str(biothings_query)

            batch_biolink_query_return_value = batch_biolink_query.pop("query")
            assert batch_biolink_query_return_value == str(biolink_query)

            batch_result = (
                base_result.json() == batch_id_query,
                base_result.json() == batch_biothings_query,
                base_result.json() == batch_biolink_query,
            )
            results_aggregation.append(batch_result)

        results_validation = []
        failure_messages = []
        for result, test_query in zip(results_aggregation, curie_id_testing_collection):
            cumulative_result = all(result)
            if not cumulative_result:
                failure_messages.append(
                    f"Query Failure: {test_query} | Results: {result}"
                )
            results_validation.append(cumulative_result)

        assert all(results_validation), "\n".join(failure_messages)
        assert all(results_validation), "\n".join(failure_messages)
