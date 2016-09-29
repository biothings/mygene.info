from .entrez_base import Gene2RefseqParser
import biothings.dataload.uploader as uploader

class EntrezRefseqUploader(uploader.BaseSourceUploader):

    name = "entrez_refseq"
    main_source = "entrez"

    def load_data(self, data_folder):
        parser = Gene2RefseqParser(data_folder)
        parser.set_all_species()
        gene2refseq = parser.load()
        return gene2refseq

    def get_mapping(self):
        mapping = {
                "refseq": {
                    "dynamic": False,
                    #"path": "just_name",      #make both fields, refseq, refseq.rna, work
                    "properties": {
                        "genomic": {
                            "type": "string",
    			"index": "no",
                            "include_in_all": False,
                            },
                        "rna": {
                            "type": "string",
                            "analyzer": "refseq_analyzer",
                            "copy_to": "refseq",
                            },
                        'protein': {
                            "type": "string",
                            "analyzer": "refseq_analyzer",
                            "copy_to": "refseq",
                            },
                        'translation': {
                            "type": "object",
                            "enabled": False,
                            "include_in_all": False,
                            },
                        }
                    }
                }
        return mapping
