import os
import os.path
import sys
import time
from datetime import datetime

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT, logger as logging
from biothings.hub.dataload.dumper import FTPDumper, FilesystemDumper
from biothings.utils.hub_db import get_src_dump


class UniprotDumper(FTPDumper):

    SRC_NAME = "uniprot"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    FTP_HOST = 'ftp.uniprot.org'
    CWD_DIR = '/pub/databases/uniprot/current_release/knowledgebase/idmapping'

    SCHEDULE = "0 6 * * *"

    def get_newest_info(self):
        res = self.client.sendcmd("MDTM idmapping_selected.tab.gz") # pick one, assuming all other on the same data
        code, remote_lastmodified = res.split()
        self.release = datetime.strptime(remote_lastmodified, '%Y%m%d%H%M%S').strftime("%Y%m%d")

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
        for fn in ["idmapping_selected.tab.gz"]:
            local_file = os.path.join(self.new_data_folder,fn)
            if force or not os.path.exists(local_file) or self.remote_is_better(fn,local_file) or self.new_release_available():
                self.to_dump.append({"remote": fn, "local":local_file})


class UniprotDependentDumper(FilesystemDumper):

    UNIPROT_FILE = None # tbd

    def create_todump_list(self, force=False):
        uni_doc = get_src_dump().find_one({"_id":UniprotDumper.SRC_NAME}) or {}
        if uni_doc:
            remotefile = os.path.join(uni_doc["data_folder"],self.__class__.UNIPROT_FILE)
            if not os.path.exists(remotefile):
                self.logger.warning("File '%s' doesn't exist (yet?)" % self.__class__.UNIPROT_FILE)
                return
            self.release = uni_doc["release"]
            localfile = os.path.join(self.current_data_folder,self.__class__.UNIPROT_FILE)
            if force or not os.path.exists(localfile) or self.remote_is_better(remotefile,localfile):
                self.to_dump.append({"remote":remotefile,"local":localfile})
        else:
            self.logger.error("Dependent uniprot datasource has not been loaded (not src_dump doc)")


class UniprotPDBDumper(UniprotDependentDumper):
    SRC_NAME = "uniprot_pdb"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    SCHEDULE = "0 11 * * *"
    UNIPROT_FILE = "gene2pdb.pyobj"


class UniprotPIRDumper(UniprotDependentDumper):
    SRC_NAME = "uniprot_pir"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    SCHEDULE = "0 11 * * *"
    UNIPROT_FILE = "gene2pir.pyobj"
