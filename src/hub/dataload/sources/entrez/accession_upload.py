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
                    #"path": "just_name",      #make both fields, accession.rna and rna, work
                    "properties": {
                        "genomic": {
                            "type": "string",
    			"index": "no",
                            "include_in_all": False,
                            },
                        "rna": {
                            "type": "string",
                            "analyzer": "refseq_analyzer",
                            },
                        'protein': {
                            "type": "string",
                            "analyzer": "refseq_analyzer",
                            #"index_name": "accession",
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

