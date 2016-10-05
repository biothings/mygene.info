
'''
#Build_Config example

Build_Config = {
    "name":     "test",          #target_collection will be called "genedoc_test"
    "sources" : ['entrez_gene', 'reporter'],
    "gene_root": ['entrez_gene', 'ensembl_gene']     #either entrez_gene or ensembl_gene or both
}

#for genedoc at mygene.info
Build_Config = {
    "name":     "mygene",          #target_collection will be called "genedoc_mygene"
    "sources":  [u'ensembl_acc',
                 u'ensembl_gene',
                 u'ensembl_genomic_pos',
                 u'ensembl_interpro',
                 u'ensembl_prosite',
                 u'entrez_accession',
                 u'entrez_ec',
                 u'entrez_gene',
                 u'entrez_genesummary',
                 u'entrez_go',
                 u'entrez_homologene',
                 u'entrez_refseq',
                 u'entrez_retired',
                 u'entrez_unigene',
                 u'pharmgkb',
                 u'reagent',
                 u'reporter',
                 u'uniprot',
                 u'uniprot_ipi',
                 u'uniprot_pdb',
                 u'uniprot_pir'],
    "gene_root": ['entrez_gene', 'ensembl_gene']
}
'''

import biothings.databuild.builder as builder

class MyGeneDataBuilder(builder.DataBuilder):

    def generate_root_document_query(self):
        """Root documents are created according to species list"""
        if "species" in self._build_config:
            _query = {'taxid': {'$in': self._build_config['species']}}
        elif "species_to_exclude" in self._build_config:
            _query = {'taxid': {'$nin': self._build_config['species_to_exclude']}}
        else:
            _query = None
        return _query


if __name__ == '__main__':
    import sys

    import biothings, config
    biothings.config_for_app(config)
    from config import LOG_FOLDER

    import biothings.utils.mongo as mongo
    import biothings.databuild.backend as btbackend
    from databuild.mapper import EntrezRetired2Current, Ensembl2Entrez

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
    source_backend =  btbackend.SourceDocMongoBackend(
                            build=mongo.get_src_build(),
                            master=mongo.get_src_master(),
                            dump=mongo.get_src_dump(),
                            sources=mongo.get_src_db())
    # declare target backend
    target_backend = btbackend.TargetDocMongoBackend(target_db=mongo.get_target_db())
    # build mapping object (ensembl -> entrez IDs conversionà
    retired2current = EntrezRetired2Current(convert_func=int,db=mongo.get_src_db())
    ensembl2entrez = Ensembl2Entrez(name="ensembl_gene",
                                    db=mongo.get_src_db(),
                                    retired2current=retired2current)
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

