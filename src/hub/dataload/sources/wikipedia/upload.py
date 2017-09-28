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
                            "copy_to": [
                                "wikipedia"
                                ],
                            "type": "string"
                            }
                        }
                    }
                }
        return mapping

