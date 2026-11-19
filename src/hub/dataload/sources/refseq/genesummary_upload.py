from .parser import GeneSummaryParser
import biothings.hub.dataload.uploader as uploader


class RefseqSummaryUploader(uploader.MergerSourceUploader):

    name = "refseq_summary"
    main_source = "refseq"

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
