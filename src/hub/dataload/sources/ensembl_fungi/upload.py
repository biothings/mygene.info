from hub.dataload.sources.ensembl.acc_upload import EnsemblAccUploader
from hub.dataload.sources.ensembl.gene_upload import EnsemblGeneUploader
from hub.dataload.sources.ensembl.genomic_pos_upload import EnsemblGenomicPosUploader
from hub.dataload.sources.ensembl.interpro_upload import EnsemblInterproUploader
from hub.dataload.sources.ensembl.pfam_upload import EnsemblPfamUploader
from hub.dataload.sources.ensembl.prosite_upload import EnsemblPrositeUploader

class EnsemblFungiAccUploader(EnsemblAccUploader):

    name = "ensembl_fungi_acc"
    main_source = "ensembl_fungi"

class EnsemblFungiGeneUploader(EnsemblGeneUploader):

    name = "ensembl_fungi_gene"
    main_source = "ensembl_fungi"


class EnsemblFungiGenomicPosUploader(EnsemblGenomicPosUploader):

    name = "ensembl_fungi_genomic_pos"
    main_source = "ensembl_fungi"


class EnsemblFungiInterproUploader(EnsemblInterproUploader):

    name = "ensembl_fungi_interpro"
    main_source = "ensembl_fungi"


class EnsemblFungiPfamUploader(EnsemblPfamUploader):

    name = "ensembl_fungi_pfam"
    main_source = "ensembl_fungi"


class EnsemblFungiPrositeUploader(EnsemblPrositeUploader):

    name = "ensembl_fungi_prosite"
    main_source = "ensembl_fungi"
