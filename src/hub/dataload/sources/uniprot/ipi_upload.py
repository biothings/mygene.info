import biothings.hub.dataload.uploader as uploader

class UniprotIPIUploader(uploader.DummySourceUploader):
    """
    Discontinued, last release was: 20140611
    """

    name = "uniprot_ipi"


    @classmethod
    def get_mapping(klass):
        mapping = {
                "ipi" : {
                    "type" : "text",
                    "analyzer" : "string_lowercase",
                    'copy_to': ['all'],
                    }
                }

        return mapping

