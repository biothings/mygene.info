import os.path
from .parser import load_data
import biothings.hub.dataload.uploader as uploader


class UMLSUploader(uploader.BaseSourceUploader):

    name = "umls"

    def load_data(self, data_folder):
        datafile = os.path.join(data_folder, 'MRCONSO.RRF')
        umls_docs = load_data(datafile)
        return umls_docs

    @classmethod
    def get_mapping(klass):
        mapping = {
            "umls": {
                "properties": {
                    "cui": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                }
            }
        }
        return mapping

