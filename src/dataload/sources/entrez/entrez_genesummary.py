from .entrez_base import GeneSummaryParser
import biothings.dataload.uploader as uploader

class EntrezGeneSummaryUploader(uploader.BaseSourceUploader):

    name = "entrez_genesummary"
    main_source = "entrez"

    def load_data(self, data_folder):
        gene2summary = GeneSummaryParser(data_folder).load()
        return gene2summary

    def get_mapping(self):
        mapping = {
            "summary": {
                "type": "string",
                "boost": 0.5      # downgrade summary field.
            },
        }
        return mapping
