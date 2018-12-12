from hub.dataload.sources.ensembl.acc_upload import EnsemblAccUploader
from hub.dataload.sources.ensembl.gene_upload import EnsemblGeneUploader
from hub.dataload.sources.ensembl.genomic_pos_upload import EnsemblGenomicPosUploader
from hub.dataload.sources.ensembl.interpro_upload import EnsemblInterproUploader
from hub.dataload.sources.ensembl.pfam_upload import EnsemblPfamUploader
from hub.dataload.sources.ensembl.prosite_upload import EnsemblPrositeUploader

class EnsemblMetazoaAccUploader(EnsemblAccUploader):

    name = "ensembl_metazoa_acc"
    main_source = "ensembl_metazoa"

class EnsemblMetazoaGeneUploader(EnsemblGeneUploader):

    name = "ensembl_metazoa_gene"
    main_source = "ensembl_metazoa"


class EnsemblMetazoaGenomicPosUploader(EnsemblGenomicPosUploader):

    name = "ensembl_metazoa_genomic_pos"
    main_source = "ensembl_metazoa"


class EnsemblMetazoaInterproUploader(EnsemblInterproUploader):

    name = "ensembl_metazoa_interpro"
    main_source = "ensembl_metazoa"


class EnsemblMetazoaPfamUploader(EnsemblPfamUploader):

    name = "ensembl_metazoa_pfam"
    main_source = "ensembl_metazoa"


class EnsemblMetazoaPrositeUploader(EnsemblPrositeUploader):

    name = "ensembl_metazoa_prosite"
    main_source = "ensembl_metazoa"
