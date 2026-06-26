from hub.dataload.sources.ensembl.acc_upload import EnsemblAccUploader
from hub.dataload.sources.ensembl.gene_upload import EnsemblGeneUploader
from hub.dataload.sources.ensembl.genomic_pos_upload import EnsemblGenomicPosUploader
from hub.dataload.sources.ensembl.interpro_upload import EnsemblInterproUploader
from hub.dataload.sources.ensembl.pfam_upload import EnsemblPfamUploader
from hub.dataload.sources.ensembl.prosite_upload import EnsemblPrositeUploader

class EnsemblPlantAccUploader(EnsemblAccUploader):

    name = "ensembl_plant_acc"
    main_source = "ensembl_plant"

    # NCBI gene ids that map to an unusually large number of Ensembl genes.
    # When the merged "ensembl" array exceeds this size, drop the id to avoid
    # bloated documents.
    EDGE_CASE_IDS = {"25016676", "25016709"}
    MAX_ENSEMBL = 10000

    def load_data(self, data_folder):
        ensembl2acc = super().load_data(data_folder)
        for _id in self.EDGE_CASE_IDS:
            doc = ensembl2acc.get(_id)
            if not doc:
                continue
            ensembl = doc.get("ensembl")
            if isinstance(ensembl, list) and len(ensembl) > self.MAX_ENSEMBL:
                self.logger.info(
                    "Dropping NCBI gene %s: ensembl array has %d entries (> %d)",
                    _id, len(ensembl), self.MAX_ENSEMBL,
                )
                del ensembl2acc[_id]
        return ensembl2acc

class EnsemblPlantGeneUploader(EnsemblGeneUploader):

    name = "ensembl_plant_gene"
    main_source = "ensembl_plant"


class EnsemblPlantGenomicPosUploader(EnsemblGenomicPosUploader):

    name = "ensembl_plant_genomic_pos"
    main_source = "ensembl_plant"


class EnsemblPlantInterproUploader(EnsemblInterproUploader):

    name = "ensembl_plant_interpro"
    main_source = "ensembl_plant"


class EnsemblPlantPfamUploader(EnsemblPfamUploader):

    name = "ensembl_plant_pfam"
    main_source = "ensembl_plant"


class EnsemblPlantPrositeUploader(EnsemblPrositeUploader):

    name = "ensembl_plant_prosite"
    main_source = "ensembl_plant"
