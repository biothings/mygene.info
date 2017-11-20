import os
import os.path
import sys
import time

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT, logger as logging
from biothings.hub.dataload.dumper import FTPDumper


class HomologeneDumper(FTPDumper):

    SRC_NAME = "homologene"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    FTP_HOST = 'ftp.ncbi.nih.gov'
    CWD_DIR = '/pub/HomoloGene/current'

    SCHEDULE = "0 6 * * *"

    def get_newest_info(self):
        rel = None
        def setrel(line):
            nonlocal rel
            rel = line
        self.client.retrlines("RETR RELEASE_NUMBER",setrel)
        self.release = rel

    def new_release_available(self):
        current_release = self.src_doc.get("release")
        if not current_release or self.release > current_release:
            self.logger.info("New release '%s' found" % self.release)
            return True
        else:
            self.logger.debug("No new release found")
            return False

    def create_todump_list(self, force=False):
        self.get_newest_info()
        remote_file = "homologene.data"
        local_file = os.path.join(self.new_data_folder,remote_file)
        if force or not os.path.exists(local_file) or self.remote_is_better(remote_file,local_file) or self.new_release_available():
            self.to_dump.append({"remote": remote_file, "local":local_file})

