import biothings.hub.dataload.uploader as uploader
from .parser import GeneSummaryParser



class NcbiGeneSummaryUploader(uploader.MergerSourceUploader):

    name = "ncbi_gene"

    def load_data(self, data_folder):
        gene2summary = GeneSummaryParser(data_folder).load()
        return gene2summary

    @classmethod
    def get_mapping(klass):
        mapping = {
            "summary": {
                "type": "text",
                "copy_to": "all"
            },
        }
        return mapping
