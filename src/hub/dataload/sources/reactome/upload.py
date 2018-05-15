from .parser import load_data
import biothings.hub.dataload.uploader as uploader

#class PharmgkbUploader(uploader.MergerSourceUploader):
class ReactomeUploader(uploader.BaseSourceUploader):

    name = "reactome"
    __metadata__ = {"merger" : "merge_struct"}

    def load_data(self, data_folder):
        return load_data(data_folder)

    @classmethod
    def get_mapping(klass):
        mapping = {
            "pathway": {
                "dynamic": False,
                "properties": {
                }
            }
        }
        mapping['pathway']['properties']["reactome"] = {
            "dynamic": False,
            "properties": {
                'id': {
                    "type": "text",
                    "copy_to": ["all"],
                },
                'name': {
                    "type": "text",
                    "copy_to": ["all"],
                }
            }
        }

        mapping["reactome"] = {
            "type": "text",
        }

        return mapping
