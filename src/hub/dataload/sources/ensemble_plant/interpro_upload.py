from hub.dataload.sources.ensembl.interpro_upload import EnsemblInterproUploader

class EnsemblPlantInterproUploader(EnsemblInterproUploader):

    name = "ensembl_plant_interpro"
    main_source = "ensembl_plant"