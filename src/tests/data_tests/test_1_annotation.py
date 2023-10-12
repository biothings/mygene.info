from biothings.tests.web import BiothingsDataTest


class TestAnnotationGET(BiothingsDataTest):
    host = "mygene.info"
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


class TestAnnotationPOST(BiothingsDataTest):
    host = "mygene.info"
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
        data = {"ids": "1017,1018", "filter": "symbol,go.MF"}
        res = self.request("gene", method="POST", data=data).json()
        assert len(res) == 2
        for _g in res:
            assert set(_g) == set(["_id", "_version", "query", "symbol", "go"])
            assert "MF" in _g["go"]

    def test_155(self):
        # get retired gene
        res = self.request("gene", method="POST", data={"ids": "791256"}).json()
        assert res[0]["_id"] == "50846"  # this is the corresponding _id field
