import biothings.hub.dataload.uploader as uploader


platform_li = [
    'CM-LibrX-no-seq',
    'CondMedia_CM_LibrAB',
    'GNF_Qia_hs-genome_v1_siRNA',
    'GNF_hs-GPCR_IDT-siRNA',
    'GNF_hs-ORFeome1_1_reads',    # original 'GNF_hs-ORFeome1.1_reads', replaced "." with "_" to make a valid key
    'GNF_hs-Origene',
    'GNF_hs-druggable_lenti-shRNA',
    'GNF_hs-druggable_plasmid-shRNA',
    'GNF_hs-druggable_siRNA',
    'GNF_hs-oncomine_IDT-siRNA',
    'GNF_hs-pkinase_IDT-siRNA',
    'GNF_hs_LentiORF-HA-MYC',
    'GNF_hs_LentiORF-Jred',
    'GNF_mm+hs-MGC',
    'GNF_mm+hs_RetroCDNA',
    'GNF_mm-GIPZ_shRNA',
    'GNF_mm-TLR_lenti_shRNA',
    'GNF_mm-kinase_lenti-shRNA',
    'GNF_mm-kinase_plasmid-shRNA',
    'IDT_27mer_hs_ATPase_siRNAs',
    'Invitrogen_IVTHSSIPKv2',
    'MasterSecretomicsList',
    'NIBRI_hs-Secretome_pDEST',
    'NOVART_hs-genome_siRNA',
    'Qiagen_mouse_QMIHSINHIBv1',
    'Qiagen_mouse_QMIHSMIMv1'
]


class ReagentUploader(uploader.DummySourceUploader):

    name = "reagent"

    def load_data(self, data_folder):
        raise Exception("Collection-only resource, no more dataload")
        genedoc_d = loadobj(os.path.join(data_folder, 'gnfreagents_20110817.pyobj'))
        #Fixing invalid key "GNF_hs-ORFeome1.1_reads" (replacing "." with "_")
        for k in genedoc_d:
            doc = genedoc_d[k]
            if "GNF_hs-ORFeome1.1_reads" in doc['reagent']:
                doc['reagent']['GNF_hs-ORFeome1_1_reads'] = doc['reagent']['GNF_hs-ORFeome1.1_reads']
                del doc['reagent']['GNF_hs-ORFeome1.1_reads']
                genedoc_d[k] = doc
        return genedoc_d

    @classmethod
    def get_mapping(klass):
        platform_mapping = {
            "dynamic": False,
            "properties": {
                "id": {
                    "type": "string",
                    "analyzer": "string_lowercase",
                },
                "relationship": {
                    "type": "string",
                    "index": "no",
                    "include_in_all": False
                }
            }
        }

        mapping = {
            "reagent": {
                "dynamic": False,
                "properties": {}
            }
        }
        for platform in platform_li:
            mapping['reagent']['properties'][platform] = platform_mapping

        return mapping
