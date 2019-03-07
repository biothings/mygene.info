from hub.dataload.sources.ensembl.acc_upload import EnsemblAccUploader
from hub.dataload.sources.ensembl.gene_upload import EnsemblGeneUploader
from hub.dataload.sources.ensembl.genomic_pos_upload import EnsemblGenomicPosUploader
from hub.dataload.sources.ensembl.interpro_upload import EnsemblInterproUploader
from hub.dataload.sources.ensembl.pfam_upload import EnsemblPfamUploader
from hub.dataload.sources.ensembl.prosite_upload import EnsemblPrositeUploader

class EnsemblProtistsAccUploader(EnsemblAccUploader):

    name = "ensembl_protists_acc"
    main_source = "ensembl_protists"

class EnsemblProtistsGeneUploader(EnsemblGeneUploader):

    name = "ensembl_protists_gene"
    main_source = "ensembl_protists"


class EnsemblProtistsGenomicPosUploader(EnsemblGenomicPosUploader):

    name = "ensembl_protists_genomic_pos"
    main_source = "ensembl_protists"


class EnsemblProtistsInterproUploader(EnsemblInterproUploader):

    name = "ensembl_protists_interpro"
    main_source = "ensembl_protists"


class EnsemblProtistsPfamUploader(EnsemblPfamUploader):

    name = "ensembl_protists_pfam"
    main_source = "ensembl_protists"


class EnsemblProtistsPrositeUploader(EnsemblPrositeUploader):

    name = "ensembl_protists_prosite"
    main_source = "ensembl_protists"
