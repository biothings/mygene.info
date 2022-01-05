import os
import json
import biothings, config
biothings.config_for_app(config)

import biothings.hub.dataload.uploader

class UniiUploader(biothings.hub.dataload.uploader.BaseSourceUploader):
    name = "mygene_unii"
    __metadata__ = {
        "src_meta": {
            "url": "https://open.fda.gov/apis/other/substance/",
            "license_url": "https://open.fda.gov/license/",
            "license": "Creative Commons CC0 1.0 Universal"
        }
    }

    idconverter = None
    storage_class = biothings.hub.dataload.storage.IgnoreDuplicatedStorage

    def load_data(self, data_folder):
        self.logger.info("Load data from directory: '%s'" % data_folder)
        infile = os.path.join(data_folder,"gene_unii.ndjson")
        assert os.path.exists(infile)
        with open(infile, 'r') as f:
            for line in f:
                yield json.loads(line)


    @classmethod
    def get_mapping(klass):
        mapping = {
            "unii": {
                "type": "keyword",
                "normalizer" : "keyword_lowercase_normalizer",
            },
        }
        return mapping
    

