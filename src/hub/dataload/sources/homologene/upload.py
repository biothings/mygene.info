from .parser import HomologeneParser
import biothings.hub.dataload.uploader as uploader

class HomologeneUploader(uploader.MergerSourceUploader):

    name = "homologene"

    def load_data(self, data_folder):
        parser = HomologeneParser(data_folder)
        parser.set_all_species()
        gene2homologene = parser.load()
        return gene2homologene

    @classmethod
    def get_mapping(klass):
        mapping = {
            "homologene": {
                "dynamic": False,
                #"path": "just_name",
                "properties": {
                    "genes": {
                        "type": "long",
                        "index": False,
                    },
                    "id": {
                        "type": "long",
                    }
                }
            }
        }
        return mapping
