from .parser import Gene2AccessionParser
import biothings.hub.dataload.uploader as uploader

class NcbiGeneAccessionUploader(uploader.MergerSourceUploader):

    name = "ncbi_gene_accession"
    main_source = "ncbi_gene"

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
                            'copy_to': ['all','accession_agg'],
                            },
                        'protein': {
                            "type": "text",
                            "analyzer": "refseq_analyzer",
                            'copy_to': ['all','accession_agg'],
                            },
                        'translation': {
                            "type": "object",
                            "enabled": False,
                            },
                        }
                    },
                "accession_agg" : {
                    'analyzer': 'refseq_analyzer',
                    'type': 'text'
                    },
                }
        return mapping

