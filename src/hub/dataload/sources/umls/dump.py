import os
import os.path
import sys
import time

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import ManualDumper
from biothings.utils.common import unzipall


class UMLSDumper(ManualDumper):

    SRC_NAME = "umls"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    def __init__(self, *args, **kwargs):
        super(UMLSDumper,self).__init__(*args,**kwargs)
        self.logger.info("""
Assuming manual download from: https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html
- umls-2017AA-full.zip
""")

    def post_dump(self, *args, **kwargs):
        self.logger.info("Unzipping files in '%s'" % self.new_data_folder) 
        unzipall(self.new_data_folder)


