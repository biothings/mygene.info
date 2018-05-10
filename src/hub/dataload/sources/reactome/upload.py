from .parser import load_data
import biothings.hub.dataload.uploader as uploader

#class PharmgkbUploader(uploader.MergerSourceUploader):
class ReactomeUploader(uploader.BaseSourceUploader):

    name = "reactome"

    def load_data(self, data_folder):
        return load_data(data_folder)

    @classmethod
    def get_mapping(klass):
        return {}
    #    mapping = {
    #        "pharmgkb": {
    #            "type": "text",
    #            "analyzer": "string_lowercase",
    #            'copy_to': ['all'],
    #        }
    #    }
    #    return mapping
