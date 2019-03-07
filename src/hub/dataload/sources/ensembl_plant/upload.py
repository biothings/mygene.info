from hub.dataload.sources.ensembl.acc_upload import EnsemblAccUploader
from hub.dataload.sources.ensembl.gene_upload import EnsemblGeneUploader
from hub.dataload.sources.ensembl.genomic_pos_upload import EnsemblGenomicPosUploader
from hub.dataload.sources.ensembl.interpro_upload import EnsemblInterproUploader
from hub.dataload.sources.ensembl.pfam_upload import EnsemblPfamUploader
from hub.dataload.sources.ensembl.prosite_upload import EnsemblPrositeUploader

class EnsemblPlantAccUploader(EnsemblAccUploader):

    name = "ensembl_plant_acc"
    main_source = "ensembl_plant"

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
