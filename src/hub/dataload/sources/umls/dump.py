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
    VERSION = '2020-4-7'

    def create_todump_list(self, force=True):
        self.release = VERSION
        local = os.path.join(SRC_ROOT_FOLDER, VERSION)
        self.to_dump.append({"remote":VERSION, "local":local})
