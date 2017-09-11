from .entrez_base import Gene2RetiredParser
import biothings.dataload.uploader as uploader

class EntrezRetiredUploader(uploader.MergerSourceUploader):

    name = "entrez_retired"
    main_source = "entrez"

    def load_data(self, data_folder):
        parser = Gene2RetiredParser(data_folder)
        parser.set_all_species()
        gene2retired = parser.load()
        return gene2retired

    def get_mapping(self):
        mapping = {
            "retired": {"type": "long"},
        }
        return mapping
