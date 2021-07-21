from biothings.tests.web import BiothingsDataTest


class TestDataFields(BiothingsDataTest):
    host = 'mygene.info'
    prefix = 'v3'

    def test_601_hg19(self):

        url = 'query?q=hg19.chr12:57,795,963-57,815,592&species=human'
        res = self.request(url).json()
        assert len(res['hits']) == 2
        assert '_id' in res['hits'][0]

    def test_602_hg19(self):
        url = 'query?q=hg19.chr12:57,795,963-57,815,592&species=human'
        res = self.request(url).json()
        url = 'query?q=chr12:57,795,963-57,815,592&species=human'
        res2 = self.request(url).json()
        assert res['total'] != res2['total']

    def test_603_hg19(self):
        url = 'query?q=hg19.chr12:57,795,963-57,815,592&species=human'
        res = self.request(url).json()
        url = 'gene/10017?fields=genomic_pos_hg19,exons_hg19'
        res = self.request(url).json()
        assert 'genomic_pos_hg19' in res
        assert 'exons_hg19' in res

    def test_604_mm9(self):
        url = 'query?q=mm9.chr12:57,795,963-57,815,592&species=mouse'
        res = self.request(url).json()
        assert len(res['hits']) == 2
        assert '_id' in res['hits'][0]

    def test_605_mm9(self):
        url = 'query?q=mm9.chr12:57,795,963-57,815,592&species=mouse'
        res = self.request(url).json()
        url = 'query?q=chr12:57,795,963-57,815,592&species=mouse'
        res2 = self.request(url).json()
        assert res['total'] != res2['total']

    def test_606_mm9(self):
        url = 'gene/12049?fields=genomic_pos_mm9,exons_mm9'
        res = self.request(url).json()
        assert 'genomic_pos_mm9' in res
        assert 'exons_mm9' in res

    def test_611_refseq(self):
        protein = filter_hits(self.request("query?q=refseq:NP_001670&fields=refseq").json())
        url = "query?q=refseq:NM_001679&fields=refseq"
        rna = filter_hits(self.request(url).json())
        genomic = filter_hits(self.request("query?q=refseq:NT_005612&fields=refseq").json())
        url = "query?q=refseq.protein:NP_001670&fields=refseq"
        explicit_protein = filter_hits(self.request(url).json())
        filter_hits(explicit_protein)
        url = "query?q=refseq.rna:NM_001679&fields=refseq"
        explicit_rna = filter_hits(self.request(url).json())
        assert protein["hits"] == explicit_protein["hits"]
        assert rna["hits"] == explicit_rna["hits"]
        assert protein["hits"] == rna["hits"]  # same result whatever the query
        assert genomic["hits"] == []  # genomic not indexed
        assert rna["total"] == 1
        hit = rna["hits"][0]
        assert hit["refseq"]["protein"] == "NP_001670.1"
        assert hit["refseq"]["rna"].startswith("NM_001679.")


    def test_615_accession(self):
        protein = filter_hits(self.request(
            "query?q=accession:AAH68303&fields=accession").json())
        rna = filter_hits(self.request("query?q=accession:BC068303&fields=accession").json())
        genomic = filter_hits(self.request(
            "query?q=accession:FJ497232&fields=accession").json())
        url = "query?q=accession.protein:AAH68303&fields=accession"
        explicit_protein = filter_hits(self.request(url).json())
        url = "query?q=accession.rna:BC068303&fields=accession"
        explicit_rna = filter_hits(self.request(url).json())
        assert protein["hits"] == explicit_protein["hits"]
        assert rna["hits"] == explicit_rna["hits"]
        assert protein["hits"] == rna["hits"]  # same result whatever the query
        assert genomic["hits"] == []  # genomic not indexed
        assert rna["total"] == 1
        hit = rna["hits"][0]
        assert "AAH68303.1" in hit["accession"]["protein"]
        assert "BC068303.1" in hit["accession"]["rna"]

    def test_620_reporter(self):
        # human
        human = self.request("query?q=reporter:2842429&fields=reporter").json()
        assert human["total"] == 3
        for hit in human["hits"]:
            if hit["_id"] == "375484":
                assert hit["reporter"]["HuGene-1_1"] == "8110147"
                assert "2889211" in hit["reporter"]["HuEx-1_0"]
                assert "TC05002114.hg.1" in hit["reporter"]["HTA-2_0"]
                assert hit["reporter"]["HG-U133_Plus_2"] == "228805_at"
                assert "gnf1h08801_at" in hit["reporter"]["GNF1H"]
                assert hit["reporter"]["HuGene-1_1"] == "8110147"
                assert hit["reporter"]["HuGene-2_1"] == "16992761"
                break
        else:
            assert False, "Expected doc not found."

    def test_621_reporter(self):
        # rat
        rat = filter_hits(self.request("query?q=reporter:1387540_at&fields=reporter").json())
        assert rat["total"] == 1
        assert rat["hits"][0]["reporter"]["RaEx-1_0"] == "7082865"
        assert rat["hits"][0]["reporter"]["Rat230_2"] == "1387540_at"
        assert rat["hits"][0]["reporter"]["RaGene-2_1"] == "17661681"
        assert rat["hits"][0]["reporter"]["RaGene-1_1"] == "10747640"
        assert "AF036760_at" in rat["hits"][0]["reporter"]["RG-U34A"]

    def test_622_reporter(self):
        mouse = filter_hits(self.request(
            "query?q=reporter:1452128_a_at&fields=reporter").json())
        assert mouse["total"] == 1
        assert "1456141_x_at" in mouse["hits"][0]["reporter"]["Mouse430_2"]
        assert mouse["hits"][0]["reporter"]["MTA-1_0"] == "TC0X00000742.mm.1"
        assert "165150_i_at" in mouse["hits"][0]["reporter"]["MG-U74Bv2"]
        assert mouse["hits"][0]["reporter"]["MoEx-1_0"] == "7012082"
        assert mouse["hits"][0]["reporter"]["GNF1M"] == "gnf1m11626_at"
        assert mouse["hits"][0]["reporter"]["MoGene-2_1"] == "17535957"
        assert mouse["hits"][0]["reporter"]["MoGene-1_1"] == "10600512"

    def test_625_interpro(self):
        res = self.request(
            "query?q=interpro:IPR008389&fields=interpro&species=human,mouse,rat").json()
        assert res["total"] == 6
        assert set([pro["id"] for hit in res["hits"]
                    for pro in hit["interpro"]]) == set(['IPR008389',
                                                         'IPR017385'])

    def test_630_go(self):
        res = self.request("query?q=GO:0016324&fields=go&sort=_id").json()
        assert res["total"] > 800

    def test_631_homologene(self):
        res = self.request(
            "query?q=homologene:44221&fields=homologene&species=human,mouse,rat").json()
        assert res["total"] == 3
        hit = res["hits"][0]
        assert set([i[0] for i in hit["homologene"]["genes"]]) == \
            set([7955, 8364, 9031, 9598, 9606, 9615, 9913, 10090, 10116])

    def test_635_reagent(self):
        res = self.request("query?q=reagent:GNF190467&fields=reagent").json()
        assert res["total"] == 1
        hit = res["hits"][0]
        assert {"relationship": "is", "id": "GNF168655"} in \
            hit["reagent"]["GNF_Qia_hs-genome_v1_siRNA"]
        assert {"relationship": "is", "id": "GNF277345"} in \
            hit["reagent"]["GNF_mm+hs-MGC"]
        assert {"relationship": "is", "id": "GNF110093"} in \
            hit["reagent"]["NOVART_hs-genome_siRNA"]

    def test_640_refseq(self):
        # no version, _all
        res = filter_hits(self.request("query?q=NM_001798&fields=refseq").json())
        hits = res["hits"]
        assert len(hits) == 1
        found = False
        for rna in hits[0]["refseq"]["rna"]:
            if rna.startswith("NM_001798."):
                found = True
                break
        assert found
        # with version, _all
        sameres = filter_hits(self.request("query?q=NM_001798.5&fields=refseq").json())
        assert sameres["hits"] == res["hits"]
        # using protein ID
        sameres = filter_hits(self.request("query?q=XP_011536034&fields=refseq").json())
        assert sameres["hits"] == res["hits"]
        # using explicit field
        sameres = filter_hits(self.request("query?q=refseq:XP_011536034&fields=refseq").json())
        assert sameres["hits"] == res["hits"]

    def test_645_exac(self):
        # (Exome Aggregation Consortium)
        res = filter_hits(self.request(
            "query?q=exac.transcript:ENST00000266970.4&fields=exac").json())
        resnover = filter_hits(self.request(
            "query?q=exac.transcript:ENST00000266970&fields=exac").json())
        assert res["hits"] == resnover["hits"]
        assert len(res["hits"]) == 1
        hit = res["hits"][0]
        assert hit["exac"]["bp"] == 897
        assert hit["exac"]["cds_end"] == 56365409
        assert hit["exac"]["cds_start"] == 56360792
        assert hit["exac"]["n_exons"] == 7
        assert hit["exac"]["transcript"] == "ENST00000266970.4"
        assert hit["exac"]["all"]["mu_syn"] == 0.00000345583178284
        assert hit["exac"]["nonpsych"]["syn_z"] == 0.0369369403215127
        assert hit["exac"]["nontcga"]["mu_mis"] == 0.00000919091133625

    def test_650_others(self):
        # this one has some
        res = self.request("gene/1017").json()
        assert "other_names" in res, "No other_names found in %s" % res
        assert "cdc2-related protein kinase" in res["other_names"]
        assert "cell division protein kinase 2" in res["other_names"]
        assert "p33 protein kinase" in res["other_names"]
        # # that one not
        # res = self.request("gene/83656").json()
        # assert "other_names" not in res
        # query by other_names:
        res = self.request("query?q=other_names:p33&size=100").json()
        assert res["total"] > 30  # currently 35...
        # assert len(res["hits"]) == 10
        ids = [h["_id"] for h in res["hits"]]
        assert "1017" in ids, "Should have 1017 in results"

    def test_655_uniprot(self):
        swissid = filter_hits(self.request("query?q=uniprot:Q8NEB7&fields=uniprot").json())
        trembid = filter_hits(self.request("query?q=uniprot:F5H2C2&fields=uniprot").json())
        assert swissid["hits"] == trembid["hits"]
        assert trembid["total"] == 1
        assert trembid["hits"][0]["uniprot"]["Swiss-Prot"] == "Q8NEB7"
        assert set(trembid["hits"][0]["uniprot"]["TrEMBL"]), \
            set(["E7EP66", "F5H2C2", "F5H3P4", "F5H5S8"])

    def test_660_ensembl(self):
        # Vertebrate
        url = "query?q=ensemblprotein:ENSP00000379391&fields=ensembl"
        prot = self.request(url).json()
        url = "query?q=ensembltranscript:ENST00000396082&fields=ensembl"
        rna = self.request(url).json()
        url = "query?q=ensemblgene:ENSG00000100373&fields=ensembl"
        gene = self.request(url).json()
        # don' compare score, useless
        for res in [prot, rna, gene]:
            res["hits"][0].pop("_score")
        assert prot["hits"] == rna["hits"]
        assert rna["hits"] == gene["hits"]
        assert rna["total"] == 1
        hit = rna["hits"][0]
        assert hit["ensembl"]["gene"] == "ENSG00000100373"
        assert "ENSP00000216211" in hit["ensembl"]["protein"]
        assert "ENST00000216211" in hit["ensembl"]["transcript"]
        # POST /gene batch
        resl = self.request("gene", method='POST', data={'ids': 'ENSG00000148795'}).json()
        assert len(resl) == 1
        res = resl[0]
        assert res["_id"] == "1586"

    def test_661_ensembl_additional(self):
        ''' DATAFIELD Ensembl Others
        Asserts the existance of the 4 other ensembl sources,
        by querying unique genes in each individual databases '''

        # Added in March 2019

        plant = "g00297"
        fungi = "ACLA_057550"
        metazoa = "ADAC005537"
        protists = "ALNC14_077170"
        sample_list = [plant, fungi, metazoa, protists]

        for sample in sample_list:
            self.query(q="ensembl.gene:" + sample, fields="ensembl")

    def test_665_pantherdb(self):
        res = self.request("gene/348158?fields=pantherdb").json()
        assert "pantherdb" in res
        assert isinstance(res["pantherdb"]["ortholog"], list)
        res = self.request(
            "query?q=pantherdb.ortholog.taxid:10090%20AND%20pantherdb.uniprot_kb:O95867").json()
        assert len(res["hits"]) == 1
        assert res["hits"][0]["_id"] == "80740"

    def test_670_pharos(self):
        # https://pharos.nih.gov/idg/about
        res = self.request("gene/56141?fields=pharos").json()
        assert res["pharos"]["target_id"] == 4745

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
