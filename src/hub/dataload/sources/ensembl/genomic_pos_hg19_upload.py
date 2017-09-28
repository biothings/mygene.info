import biothings.hub.dataload.uploader as uploader

class EnsemblGenomicPosHg19Uploader(uploader.DummySourceUploader):

    name = "ensembl_genomic_pos_hg19"

    @classmethod
    def get_mapping(klass):
        mapping = {
                "genomic_pos_hg19" : {
                    "dynamic" : False,
                    "type" : "nested",
                    "properties" : {
                        "start" : {
                            "type" : "long"
                            },
                        "chr" : {
                            "type" : "string"
                            },
                        "end" : {
                            "type" : "long"
                            },
                        "strand" : {
                            "index" : "no",
                            "type" : "byte"
                            }
                        }
                    }
                }
        return mapping

