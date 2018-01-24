import biothings.utils.mongo as mongo
import biothings.hub.databuild.builder as builder
from biothings.utils.common import loadobj

from hub.dataload.sources.entrez.gene_upload import EntrezGeneUploader
from hub.dataload.sources.ensembl.gene_upload import EnsemblGeneUploader

class MyGeneDataBuilder(builder.DataBuilder):

    def generate_document_query(self, src_name):
        """Root documents are created according to species list"""
        _query = None
        if src_name in self.get_root_document_sources():
            if "species" in self.build_config:
                _query = {'taxid': {'$in': list(map(int,self.build_config['species']))}}
            elif "species_to_exclude" in self.build_config:
                _query = {'taxid': {'$nin': list(map(int,self.build_config['species_to_exclude']))}}
            else:
                _query = None
        if _query:
            self.logger.debug("Source '%s' requires custom query: '%s'" % (src_name,_query))
        return _query

    def document_cleaner(self,src_name,*args,**kwargs):
        # only root sources document can keep their taxid
        if src_name in self.get_root_document_sources():
            return None
        else:
            return cleaner

    def post_merge(self, source_names, batch_size, job_manager):
        self.logger.info("Indexing 'taxid'")
        # background=true or it'll lock the whole database...
        tgt = mongo.get_target_db()[self.target_name]
        tgt.create_index("taxid",background=True)

    def get_stats(self,sources,job_manager):
        self.stats = super(MyGeneDataBuilder,self).get_stats(sources,job_manager)
        # enrich with some specific mygene counts, specially regarding ensembl vs. entrez
        entrez_col = mongo.get_src_db()[EntrezGeneUploader.name]
        ensembl_col = mongo.get_src_db()[EnsemblGeneUploader.name]
        tgt = mongo.get_target_db()[self.target_name]
        mapped = len(loadobj(("ensembl_gene__2entrezgene_list.pyobj", mongo.get_src_db()), mode='gridfs'))
        self.stats["total_genes"] = tgt.count()
        self.stats["total_entrez_genes"] = entrez_col.count()
        self.stats["total_ensembl_genes"] = ensembl_col.count()
        self.stats["total_ensembl_genes_mapped_to_entrez"] = mapped
        self.stats["total_ensembl_only_genes"] = ensembl_col.count() - mapped
        self.stats["total_species"] = len(tgt.distinct("taxid"))

        return self.stats


def cleaner(doc):
    doc.pop('taxid', None)
    return doc
