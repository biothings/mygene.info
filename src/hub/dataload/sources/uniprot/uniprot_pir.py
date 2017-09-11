from .uniprot_base import load_pir
import biothings.dataload.uploader as uploader


class UniprotPIRUploader(uploader.MergerSourceUploader):

    name = "uniprot_pir"
    main_source = "uniprot"

    def load_data(self, data_folder):
        return load_pir(data_folder)

    def get_mapping(self):
        mapping = {
            "pir": {
                "type": "string",
                "analyzer": "string_lowercase"
            }
        }
        return mapping
