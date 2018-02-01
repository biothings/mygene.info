from .parser import Gene2AccessionParser
import biothings.hub.dataload.uploader as uploader

class EntrezAccessionUploader(uploader.MergerSourceUploader):

    name = "entrez_accession"
    main_source = "entrez"

    def load_data(self, data_folder):
        self.parser = Gene2AccessionParser(data_folder)
        self.parser.set_all_species()
        gene2acc = self.parser.load()
        return gene2acc

    @classmethod
    def get_mapping(klass):
        mapping = {
                "accession": {
                    "dynamic": False,
                    #make both fields, accession.rna and rna, work
                    "properties": {
                        "genomic": {
                            "type": "text",
                            "index": False,
                            },
                        "rna": {
                            "type": "text",
                            "analyzer": "refseq_analyzer",
                            'copy_to': ['all'],
                            },
                        'protein': {
                            "type": "text",
                            "analyzer": "refseq_analyzer",
                            'copy_to': ['all'],
                            },
                        'translation': {
                            "type": "object",
                            "enabled": False,
                            },
                        }
                    }
                }
        return mapping

