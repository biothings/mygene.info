from hub.dataload.sources.ensembl.genomic_pos_upload import EnsemblGenomicPosUploader

class EnsemblPlantGenomicPosUploader(EnsemblGenomicPosUploader):

    name = "ensembl_plant_genomic_pos"
    main_source = "ensembl_plant"