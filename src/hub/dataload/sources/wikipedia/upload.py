import biothings.hub.dataload.uploader as uploader

class WikipediaUploader(uploader.DummySourceUploader):

    name = "wikipedia"

    @classmethod
    def get_mapping(klass):
        mapping = {
                "wikipedia": {
                    "dynamic": False,
                    "properties": {
                        "url_stub": {
                            "type": "text",
                            'copy_to': ['all'],
                            }
                        }
                    }
                }
        return mapping

