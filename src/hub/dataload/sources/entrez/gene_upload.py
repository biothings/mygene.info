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
                "type": "text",
                "analyzer": "string_lowercase",
                'copy_to': ['all'],
            },
            "taxid": {
                "type": "integer",
            },
            "alias": {
                "type": "text",
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
                "type": "text",
                "analyzer": "string_lowercase",
                "boost": 5.0,
                'copy_to': ['all'],
            },
            "locus_tag": {
                "type": "text",
                "analyzer": "string_lowercase",
                'copy_to': ['all'],
            },

            # do not index map_location and type_of_gene
            "map_location": {
                "index": False,
                "type": "text",
            },
            "type_of_gene": {
                'analyzer': 'string_lowercase',
                "type": "text",
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
                "type": "text",              # 1771
                'analyzer': 'string_lowercase',
            },
            "HPRD": {
                "type": "text",              # 00310
                'analyzer': 'string_lowercase',
            },
            "MIM": {
                "type": "text",              # 116953
                'analyzer': 'string_lowercase',
            },
            "MGI": {
                "type": "text",              # MGI:104772
                'analyzer': 'string_lowercase',
            },
            "RATMAP": {
                "type": "text",
                'analyzer': 'string_lowercase',
            },
            "RGD": {
                "type": "text",             # 70486
                'analyzer': 'string_lowercase',
            },
            "FLYBASE": {
                "type": "text",            # FBgn0004107
                'analyzer': 'string_lowercase',
            },
            "WormBase": {
                "type": "text",         # WBGene00000871
                "analyzer": "string_lowercase",
            },
            "TAIR": {
                "type": "text",             # AT3G48750
                "analyzer": "string_lowercase",
            },
            "ZFIN": {
                "type": "text",             # ZDB-GENE-040426-2741
                "analyzer": "string_lowercase",
            },
            "Xenbase": {
                "type": "text",
                "analyzer": "string_lowercase",
            },
            "miRBase": {
                "type": "text",
                "analyzer": "string_lowercase",
            },
        }
        return mapping
