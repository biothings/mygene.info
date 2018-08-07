from .parser import GeneInfoParser
from .parser import get_geneid_d
import biothings.hub.dataload.uploader as uploader
from biothings.utils.common import dump2gridfs

class EntrezGeneUploader(uploader.MergerSourceUploader):

    name = "entrez_gene"
    main_source = "entrez"
    ENTREZ_GENEDOC_ROOT = True

    def load_data(self, data_folder):
        self.parser = GeneInfoParser(data_folder)
        self.parser.set_all_species()
        genedoc_d = self.parser.load()
        return genedoc_d

    def get_geneid_d(self,*args,**kwargs):
        return get_geneid_d(self.data_folder, *args, **kwargs)

    def post_update_data(self,*args,**kwargs):
        self.logger.info('Uploading "geneid_d" to GridFS...')
        geneid_d = self.get_geneid_d(load_cache=False,save_cache=False)
        dump2gridfs(geneid_d, self.name + '__geneid_d.pyobj', self.db)
        for field in ["MGI","HGNC","RGD","TAIR","WormBase","ZFIN","SGD","FLYBASE"]:
            self.logger.info("Indexing '%s'" % field)
            self.collection.create_index(field,background=True)

    @classmethod
    def get_mapping(klass):
        mapping = {
            "entrezgene": {
                "type": "keyword",
                "normalizer" : "keyword_lowercase_normalizer",
                'copy_to': ['all'],
            },
            "taxid": {
                "type": "integer",
            },
            "alias": {
                "type": "keyword",
                "normalizer" : "keyword_lowercase_normalizer",
                'copy_to': ['all'],
            },
            "name": {
                "type": "text",
                "boost": 0.8,    # downgrade name field a little bit
                'copy_to': ['all'],
            },
            "other_names": {
                "type": "text",
                'copy_to': ['all'],
            },
            "symbol": {
                "type": "keyword",
                "normalizer" : "keyword_lowercase_normalizer",
                "boost": 5.0,
                'copy_to': ['all'],
            },
            "locus_tag": {
                "type": "keyword",
                "normalizer" : "keyword_lowercase_normalizer",
                'copy_to': ['all'],
            },

            # do not index map_location and type_of_gene
            "map_location": {
                "index": False,
                "type": "text",
            },
            "type_of_gene": {
                "normalizer" : "keyword_lowercase_normalizer",
                "type": "keyword",
            },
            "AnimalQTLdb": {
                "index": False,
                "type": "text",
            },
            "Vega": {
                "index": False,
                "type": "text",
            },

            # convert index_name to lower-case, and excluded from "_all"
            "HGNC": {
                "type": "keyword",              # 1771
                "normalizer" : "keyword_lowercase_normalizer",
            },
            "HPRD": {
                "type": "keyword",              # 00310
                "normalizer" : "keyword_lowercase_normalizer",
            },
            "MIM": {
                "type": "keyword",              # 116953
                "normalizer" : "keyword_lowercase_normalizer",
            },
            "MGI": {
                "type": "keyword",              # MGI:104772
                "normalizer" : "keyword_lowercase_normalizer",
            },
            "RATMAP": {
                "type": "keyword",
                "normalizer" : "keyword_lowercase_normalizer",
            },
            "RGD": {
                "type": "keyword",             # 70486
                "normalizer" : "keyword_lowercase_normalizer",
            },
            "FLYBASE": {
                "type": "keyword",            # FBgn0004107
                "normalizer" : "keyword_lowercase_normalizer",
            },
            "WormBase": {
                "type": "keyword",         # WBGene00000871
                "normalizer" : "keyword_lowercase_normalizer",
            },
            "TAIR": {
                "type": "keyword",             # AT3G48750
                "normalizer" : "keyword_lowercase_normalizer",
            },
            "ZFIN": {
                "type": "keyword",             # ZDB-GENE-040426-2741
                "normalizer" : "keyword_lowercase_normalizer",
            },
            "Xenbase": {
                "type": "keyword",
                "normalizer" : "keyword_lowercase_normalizer",
            },
            "miRBase": {
                "type": "keyword",
                "normalizer" : "keyword_lowercase_normalizer",
            },
        }
        return mapping
