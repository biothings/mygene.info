import os
import os.path
import sys
import time

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT, logger as logging
from biothings.hub.dataload.dumper import FTPDumper


class ExacDumper(FTPDumper):

    SRC_NAME = "exac"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    FTP_HOST = 'ftp.broadinstitute.org'
    CWD_DIR = '/pub/ExAC_release/current/functional_gene_constraint'

    #SCHEDULE = "0 6 * * *"

    def get_newest_info(self):
        self.client.cwd("/pub/ExAC_release")
        releases = self.client.nlst()
        # stick to release 0.3.x
        releases = [x.lstrip("release") for x in releases if x.startswith('release0.3')]
        # sort items based on date
        releases = sorted(releases)
        # get the last item in the list, which is the latest version
        self.release = releases[-1]

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
        for fn in ["fordist_cleaned_exac_nonTCGA_z_pli_rec_null_data.txt",
                "fordist_cleaned_exac_r03_march16_z_pli_rec_null_data.txt",
                "fordist_cleaned_nonpsych_z_pli_rec_null_data.txt"]:
            local_file = os.path.join(self.new_data_folder,fn)
            if force or not os.path.exists(local_file) or self.remote_is_better(fn,local_file) or self.new_release_available():
                self.to_dump.append({"remote": fn, "local":local_file})

