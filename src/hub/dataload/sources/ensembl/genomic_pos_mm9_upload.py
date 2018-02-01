import biothings.hub.dataload.uploader as uploader

class EnsemblGenomicPosMM9Uploader(uploader.DummySourceUploader):

    name = "ensembl_genomic_pos_mm9"

    @classmethod
    def get_mapping(klass):
        mapping = {
                "genomic_pos_mm9" : {
                    "dynamic" : False,
                    "type" : "nested",
                    "properties" : {
                        "start" : {
                            "type" : "long"
                            },
                        "chr" : {
                            "type" : "text"
                            },
                        "end" : {
                            "type" : "long"
                            },
                        "strand" : {
                            "index" : False,
                            "type" : "byte"
                            }
                        }
                    }
                }

        return mapping

