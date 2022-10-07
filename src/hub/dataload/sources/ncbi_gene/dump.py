import os
import os.path
import sys
import time
from datetime import datetime

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT, logger as logging
from biothings.hub.dataload.dumper import FTPDumper


class NcbiGeneDumper(FTPDumper):

    SRC_NAME = "ncbi_gene"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    FTP_HOST = 'ftp.ncbi.nih.gov'
    CWD_DIR = '/gene/DATA/ASN_BINARY/Mammalia'

    SCHEDULE = "0 6 * * 6"

    def get_newest_info(self):
        res = self.client.sendcmd("MDTM All_Mammalia.ags.gz")
        code, remote_lastmodified = res.split()
        self.release = datetime.strptime(remote_lastmodified, '%Y%m%d%H%M%S').strftime("%Y%m%d")

    def new_release_available(self):
        current_release = self.src_doc.get("download",{}).get("release")
        if not current_release or self.release > current_release:
            self.logger.info("New release '%s' found" % self.release)
            return True
        else:
            self.logger.debug("No new release found")
            return False

    def create_todump_list(self, force=False, **kwargs):
        self.get_newest_info()
        for fn in ['All_Mammalia.ags.gz']:
            local_file = os.path.join(self.new_data_folder,fn)
            if force or not os.path.exists(local_file) or self.remote_is_better(fn,local_file) or self.new_release_available():
                self.to_dump.append({"remote": fn, "local":local_file})

    def post_dump(self, *args, **kwargs):
        self.logger.info("Extracting Gene Summary Data in %s", self.new_data_folder)
        os.chdir(self.new_data_folder)
        os.system('time gunzip -c All_Mammalia.ags.gz |../gene2xml -i stdin -b T | ../xtract -pattern Entrezgene -element Gene-track_geneid,Entrezgene_summary | awk -F "\t" \'length($2)\' | xz -9 --stdout > gene2summary_all.txt.xz')

