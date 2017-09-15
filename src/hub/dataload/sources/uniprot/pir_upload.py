from .parser import load_pir
import biothings.hub.dataload.uploader as uploader


class UniprotPIRUploader(uploader.MergerSourceUploader):

    name = "uniprot_pir"
    main_source = "uniprot"

    def load_data(self, data_folder):
        return load_pir(data_folder)

    @classmethod
    def get_mapping(klass):
        mapping = {
            "pir": {
                "type": "string",
                "analyzer": "string_lowercase"
            }
        }
        return mapping
