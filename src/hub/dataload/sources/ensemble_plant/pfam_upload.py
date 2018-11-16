from hub.dataload.sources.ensembl.pfam_upload import EnsemblPfamUploader

class EnsemblPlantPfamUploader(EnsemblPfamUploader):

    name = "ensembl_plant_pfam"
    main_source = "ensembl_plant"