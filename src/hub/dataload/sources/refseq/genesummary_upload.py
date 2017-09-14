from .parser import GeneSummaryParser
import biothings.hub.dataload.uploader as uploader

class EntrezGeneSummaryUploader(uploader.MergerSourceUploader):

    name = "entrez_genesummary"
    main_source = "refseq"

    def load_data(self, data_folder):
        gene2summary = GeneSummaryParser(data_folder).load()
        return gene2summary

    @classmethod
    def get_mapping(klass):
        mapping = {
            "summary": {
                "type": "string",
                "boost": 0.5      # downgrade summary field.
            },
        }
        return mapping
