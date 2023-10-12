from biothings.tests.web import BiothingsDataTest


class TestMygeneWeb(BiothingsDataTest):
    host = "mygene.info"
    prefix = "v3"

    def test_301_status(self):
        self.request("/status")

    def test_302_status(self):
        self.request("/status", method="HEAD")

    def test_311_static(self):
        self.request("/favicon.ico")

    def test_312_static(self):
        self.request("/robots.txt")

    def test_321_metadata(self):
        root_res = self.request("/metadata").json()
        api_res = self.request("metadata").json()
        assert root_res == api_res
        available_fields = {
            "build_version",
            "build_date",
            "taxonomy",
            "stats",
            "genome_assembly",
            "src",
            "biothing_type",
        }
        assert root_res.keys() == available_fields

    def test_322_metadata(self):
        fields = self.request("metadata/fields").json()
        # test random field
        assert "refseq" in fields
        assert "accession.rna" in fields
        assert "interpro.desc" in fields
        assert "homologene" in fields
        assert "reporter.snowball" in fields

    def test_323_metadata(self):
        # debug info
        debug = self.request("metadata?dev=1").json()
        assert "software" in debug.keys()
        nodebug = self.request("metadata?dev=0").json()
        assert "software" not in nodebug.keys()

    def test_331_taxonomy(self):
        res = self.request("species/1239").json()
        assert "lineage" in res

    def test_332_taxonomy(self):
        res = self.request("species/1280?include_children=true").json()
        assert len(res["children"]) >= 305

    def test_333_taxonomy(self):
        res = self.request("species/1280?include_children=true").json()
        res2 = self.request("species/1280?include_children=true&has_gene=1").json()
        assert len(res2["children"]) >= 11
        assert len(res2["children"]) <= len(res["children"])

    def test_341_species(self):
        dic = self.request("species/9606").json()
        assert set(dic.keys()) == {
            "taxid",
            "authority",
            "lineage",
            "_id",
            "genbank_common_name",
            "_version",
            "parent_taxid",
            "scientific_name",
            "has_gene",
            "children",
            "rank",
            "uniprot_name",
        }
