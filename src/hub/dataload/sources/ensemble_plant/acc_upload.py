from hub.dataload.sources.ensembl.acc_upload import EnsemblAccUploader

class EnsemblPlantAccUploader(EnsemblAccUploader):

    name = "ensembl_plant_acc"
    main_source = "ensembl_plant"
