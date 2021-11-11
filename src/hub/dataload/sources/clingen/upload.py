import os

import biothings, config
biothings.config_for_app(config)

import biothings.hub.dataload.uploader

# when code is exported, import becomes relative
try:
    from ClinGen.parser import load_data as parser_func
except ImportError:
    from .parser import load_data as parser_func


class ClingenUploader(biothings.hub.dataload.uploader.BaseSourceUploader):

    name = "clingen"
    __metadata__ = {
        "src_meta": {
            'license_url': 'https://www.clinicalgenome.org/docs/terms-of-use/',
            'licence': 'CC0 1.0 Universal',
            'url': 'https://search.clinicalgenome.org/kb/gene-validity'
        }
    }
    idconverter = None
    storage_class = biothings.hub.dataload.storage.IgnoreDuplicatedStorage

    def load_data(self, data_folder):
        self.logger.info("Load data from directory: '%s'" % data_folder)
        return parser_func(data_folder)

    @classmethod
    def get_mapping(klass):
        return {
            'clingen': {
                'properties': {
                    'clinical_validity': {
                        'properties': {
                            'classification': {
                                'normalizer': 'keyword_lowercase_normalizer',
                                'type': 'keyword'
                            },
                            'classification_date': {
                                "type": "date"
                            },
                            'disease_label': {
                                'type': 'text'
                            },
                            "gcep": {
                                "type": "text"
                            },
                            'mondo': {
                                'copy_to': ['all'],
                                'normalizer': 'keyword_lowercase_normalizer',
                                'type': 'keyword'
                            },
                            "moi": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            'online_report': {
                                'index': False,
                                'type': 'text'
                            },
                            'sop': {
                                'normalizer': 'keyword_lowercase_normalizer',
                                'type': 'keyword'
                            }
                        }
                    }
                }
            }
        }

