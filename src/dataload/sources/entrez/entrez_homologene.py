from .entrez_base import HomologeneParser
import biothings.dataload.uploader as uploader

class EntrezHomologeneUploader(uploader.BaseSourceUploader):

    name = "entrez_homologene"
    main_source = "entrez"

    def load_data(self, data_folder):
        parser = HomologeneParser(data_folder)
        parser.set_all_species()
        gene2homologene = parser.load()
        return gene2homologene

    def get_mapping(self):
        mapping = {
            "homologene": {
                "dynamic": False,
                #"path": "just_name",
                "properties": {
                    "genes": {
                        "type": "long",
                        "index": "no",
                        "include_in_all": False,
                    },
                    "id": {
                        "type": "long",
                        "include_in_all": False,
                        "copy_to": "homologene"
                    }
                }
            }
        }
        return mapping
