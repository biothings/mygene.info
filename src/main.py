import hub.dataload.sources.plant_ensembl.dumper
d = hub.dataload.sources.plant_ensembl.dumper.EnsemblPlantBioMart()
d.__class__.species_li.append(["arabidopsis_thaliana","Arabidopsis thaliana",3702])
d.get_gene__main("/tmp/out")
