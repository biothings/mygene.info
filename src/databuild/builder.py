
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

    def generate_document_query(self, src_name):
        """Root documents are created according to species list"""
        _query = None
        if src_name in self.get_root_document_sources():
            if "species" in self._build_config:
                _query = {'taxid': {'$in': self._build_config['species']}}
            elif "species_to_exclude" in self._build_config:
                _query = {'taxid': {'$nin': self._build_config['species_to_exclude']}}
            else:
                _query = None
        if _query:
            self.logger.debug("Source '%s' requires custom query: '%s'" % (src_name,_query))
        return _query

    def clean_document_to_merge(self,doc):
        doc.pop('taxid', None)
        return doc


