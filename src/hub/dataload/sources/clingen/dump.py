import os

import biothings, config
biothings.config_for_app(config)
from config import DATA_ARCHIVE_ROOT

from biothings.utils.common import uncompressall

import biothings.hub.dataload.dumper


class ClingenDumper(biothings.hub.dataload.dumper.LastModifiedHTTPDumper):

    SRC_NAME = "clingen"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    SCHEDULE = None
    UNCOMPRESS = False
    SRC_URLS = ['https://search.clinicalgenome.org/kb/gene-validity/download']
    SCHEDULE = "0 6 * * *"
    __metadata__ = {
        "src_meta": {
            'license_url': 'https://www.clinicalgenome.org/docs/terms-of-use/',
            'licence': 'CC0 1.0 Universal',
            'url': 'https://search.clinicalgenome.org/kb/gene-validity'
        }
    }

    def post_dump(self, *args, **kwargs):
        if self.__class__.UNCOMPRESS:
            self.logger.info("Uncompress all archive files in '%s'" %
                             self.new_data_folder)
            uncompressall(self.new_data_folder)

    def get_release(self):
        """
        return the most updated version
        """

        import requests
        import re

        response = self.client.head(self.SRC_URLS[0])
        text = response.headers["Content-Disposition"]
        date = re.findall(r'\d{4}-\d\d-\d\d', text)

        return date[0]

    def set_release(self):
        self.release = self.get_release()
