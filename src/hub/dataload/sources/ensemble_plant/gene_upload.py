from hub.dataload.sources.ensembl.gene_upload import EnsemblGeneUploader

class EnsemblPlantGeneUploader(EnsemblGeneUploader):

    name = "ensembl_plant_gene"
    main_source = "ensembl_plant"