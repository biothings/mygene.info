#!/usr/bin/env python

if __name__ == '__main__':
    import sys

    import biothings, config
    biothings.config_for_app(config)
    from config import LOG_FOLDER

    import biothings.utils.mongo as mongo
    import biothings.databuild.backend as backend
    from databuild.mapper import EntrezRetired2Current, Ensembl2Entrez
    from databuild.backend import MyGeneTargetDocMongoBackend
    from databuild.builder import MyGeneDataBuilder

    if len(sys.argv) > 1:
        build_name = sys.argv[1]
    else:
        build_name = 'mygene_allspecies'
    use_parallel = '-p' in sys.argv
    sources = None  # will build all sources
    target = None   # will generate a new collection name
    # "target_col:src_col1,src_col2" will specifically merge src_col1
    # and src_col2 into existing target_col (instead of merging everything)
    if not use_parallel and len(sys.argv) > 2:
        target,tmp = sys.argv[2].split(":")
        sources = tmp.split(",")

    # declare source backend
    source_backend =  backend.SourceDocMongoBackend(
                            build=mongo.get_src_build(),
                            master=mongo.get_src_master(),
                            dump=mongo.get_src_dump(),
                            sources=mongo.get_src_db())
    # declare target backend
    target_backend = MyGeneTargetDocMongoBackend(target_db=mongo.get_target_db())
    # build mapping object (ensembl -> entrez IDs conversionà
    from databuild.mapper import EntrezRetired2Current, Ensembl2Entrez, Ensembl2EntrezRoot
    retired2current = EntrezRetired2Current(convert_func=int,db=mongo.get_src_db())
    ensembl2entrez = Ensembl2Entrez(db=mongo.get_src_db(),
                                    retired2current=retired2current)
    ensembl2entreroot = Ensembl2EntrezRoot(ensembl2entrez=ensembl2entrez)

    # assemble the whole
    bdr = MyGeneDataBuilder(
            build_name,
            doc_root_key="gene_root",
            source_backend=source_backend,
            target_backend=target_backend,
            log_folder=config.LOG_FOLDER,
            id_mappers=[ensembl2entrez])
    # and start merging process
    bdr.merge(sources=sources,target_name=target)


