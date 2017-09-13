from .parser import Gene2UnigeneParser
import biothings.hub.dataload.uploader as uploader


class EntrezUnigeneUploader(uploader.MergerSourceUploader):

    name = "entrez_unigene"
    main_source = "entrez"

    def load_data(self, data_folder):
        self.parser = Gene2UnigeneParser(data_folder)
        self.parser.set_all_species()
        gene2unigene = self.parser.load()
        return gene2unigene

    @classmethod
    def get_mapping(klass):
        mapping = {
            "unigene":  {
                "type": "string",
                "analyzer": "string_lowercase"
            }
        }
        return mapping
