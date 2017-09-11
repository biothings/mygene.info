from .ensembl_base import EnsemblParser
import biothings.dataload.uploader as uploader

class EnsemblPfamUploader(uploader.MergerSourceUploader):

    name = "ensembl_pfam"
    main_source = "ensembl"

    def load_data(self, data_folder):
        ep = EnsemblParser(data_folder)
        ensembl2pfam = ep.load_ensembl2pfam()
        return ensembl2pfam

    def get_mapping(self):
        mapping = {
            "pfam": {
                "type": "string",
                "analyzer": "string_lowercase"
            }
        }
        return mapping
