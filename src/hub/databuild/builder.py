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
        tgt = mongo.get_target_db()[self.target_name]
        # background=true or it'll lock the whole database...
        self.logger.info("Indexing 'taxid'")
        tgt.create_index("taxid",background=True)

    def get_stats(self,sources,job_manager):
        self.stats = super(MyGeneDataBuilder,self).get_stats(sources,job_manager)
        # enrich with some specific mygene counts, specially regarding ensembl vs. entrez
        tgt = mongo.get_target_db()[self.target_name]
        self.stats["total_genes"] = tgt.count()
        # entrez genes are digits only (also, don't count entrez_gene collection,
        # because tgt can be a subset, we have to work with the merged collection)
        self.logger.debug("Counting 'total_entrez_genes'")
        entrez_cnt = tgt.find({"_id":{"$regex":'''^\\d+$'''}},{"_id":1}).count()
        self.stats["total_entrez_genes"] = entrez_cnt
        # ensembl genes aount are taken from :
        # 1. "ensembl" field, but it can a list => use aggregation. 
        #    Note: "ensembl.0" means first element of the list, so it implicitely
        #    select doc with a list. Finally, filtering with {$type:"array"} doesn't work because
        #    mongo filters this on the most inner field (that's weird, but it is what is it...)
        # 2. when document is root doc coming from ensembl_gene collection without a "ensembl" key ("orphan")
        # Note: we can't create a sparce or conditional index to help querying "ensembl"
        # because data is too long for an index key, and "hashed" mode doesn't work because list aren't supported
        # Queries are gonna use colscan strategy...
        self.logger.debug("Counting 'total_ensembl_genes'")
        res = tgt.aggregate([
            {"$match" : {"ensembl.0" : {"$exists" : True}}},
            {"$project" : {"num_gene" : {"$size" : "$ensembl"}}},
            {"$group" : {"_id" : None, "sum" : {"$sum": "$num_gene"}}}
            ])
        list_count = next(res)["sum"]
        object_count = tgt.find({"ensembl" : {"$type" : "object"}},{"_id":1}).count()
        orphan_count = tgt.find({"_id":{"$regex":'''\\w'''},"ensembl":{"$exists":0}},{"_id":1}).count()
        total_ensembl_genes = list_count + object_count + orphan_count
        self.stats["total_ensembl_genes"] = total_ensembl_genes
        # this one can't be computed from merged collection, and is only valid when build
        # involves all data (no filter, no subset)
        self.logger.debug("Counting 'total_ensembl_genes_mapped_to_entrez'")
        mapped = len(loadobj(("ensembl_gene__2entrezgene_list.pyobj", mongo.get_src_db()), mode='gridfs'))
        self.stats["total_ensembl_genes_mapped_to_entrez"] = mapped
        # ensembl gene contains letters (if it wasn't, it means it would only contain digits
        # so it would be an entrez gene (\\D = non-digits, can't use \\w as a digit *is* a letter)
        self.logger.debug("Counting 'total_ensembl_only_genes'")
        ensembl_unmapped = entrez_cnt = tgt.find({"_id":{"$regex":'''\\D'''}},{"_id":1}).count()
        self.stats["total_ensembl_only_genes"] = ensembl_unmapped
        self.logger.debug("Counting 'total_species'")
        self.stats["total_species"] = len(tgt.distinct("taxid"))

        return self.stats


def cleaner(doc):
    doc.pop('taxid', None)
    return doc
