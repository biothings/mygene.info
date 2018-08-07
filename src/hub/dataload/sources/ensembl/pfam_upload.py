from .parser import EnsemblParser
import biothings.hub.dataload.uploader as uploader

class EnsemblPfamUploader(uploader.MergerSourceUploader):

    name = "ensembl_pfam"
    main_source = "ensembl"

    def load_data(self, data_folder):
        ep = EnsemblParser(data_folder)
        ensembl2pfam = ep.load_ensembl2pfam()
        return ensembl2pfam

    @classmethod
    def get_mapping(klass):
        mapping = {
            "pfam": {
                "type": "keyword",
                "normalizer" : "keyword_lowercase_normalizer",
                'copy_to': ['all'],
            }
        }
        return mapping
