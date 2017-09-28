from .parser import Gene2RetiredParser
import biothings.hub.dataload.uploader as uploader

class EntrezRetiredUploader(uploader.MergerSourceUploader):

    name = "entrez_retired"
    main_source = "entrez"

    def load_data(self, data_folder):
        parser = Gene2RetiredParser(data_folder)
        parser.set_all_species()
        gene2retired = parser.load()
        return gene2retired

    @classmethod
    def get_mapping(klass):
        mapping = {
            "retired": {"type": "long"},
        }
        return mapping
