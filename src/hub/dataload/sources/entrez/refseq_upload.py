from .parser import Gene2RefseqParser
import biothings.hub.dataload.uploader as uploader

class EntrezRefseqUploader(uploader.MergerSourceUploader):

    name = "entrez_refseq"
    main_source = "entrez"

    def load_data(self, data_folder):
        parser = Gene2RefseqParser(data_folder)
        parser.set_all_species()
        gene2refseq = parser.load()
        return gene2refseq

    @classmethod
    def get_mapping(klass):
        mapping = {
                "refseq": {
                    "dynamic": False,
                    #"path": "just_name",      #make both fields, refseq, refseq.rna, work
                    "properties": {
                        "genomic": {
                            "type": "text",
                            "index": False,
                            },
                        "rna": {
                            "type": "text",
                            "analyzer": "refseq_analyzer",
                            'copy_to': ['all','refseq_agg'],
                            },
                        'protein': {
                            "type": "text",
                            "analyzer": "refseq_analyzer",
                            'copy_to': ['all','refseq_agg']
                            },
                        'translation': {
                            "type": "object",
                            "enabled": False,
                            },
                        }
                    },
                "refseq_agg" : {
                    'analyzer': 'refseq_analyzer',
                    'type': 'text'
                    },
                }
        return mapping
