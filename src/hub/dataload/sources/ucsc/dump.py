# http://hgdownload.soe.ucsc.edu/goldenPath/hg19/database/

# Copyright [2010-2013] [Chunlei Wu]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os
import os.path
import time
from datetime import datetime
from ftplib import error_perm

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT, logger as logging
from biothings.hub.dataload.dumper import FTPDumper


class UCSCDumper(FTPDumper):

    SRC_NAME = "ucsc"
    FTP_HOST = 'hgdownload.cse.ucsc.edu'
    CWD_DIR = 'goldenPath/currentGenomes'
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    latest_lastmodified = None   # record the lastmodified for the newest file.
    MAX_PARALLEL_DUMP = 1 # throttling as ucsc ftp would kick us out if too many...
    SCHEDULE = "0 6 * * *"
    ARCHIVE = False

    def get_new_data_folder(self):
        # no archive, no "latest", just keep the root directory
        return self.SRC_ROOT_FOLDER

    def get_ftpfile_lastmodified(self, file_path):
        '''return lastmodified for a given file on ftp server.'''
        try:
            response = self.client.sendcmd('MDTM ' + file_path)
        except error_perm as e:
            self.logger.debug("Skip %s: %s" % (file_path,e))
            return None
        code, lastmodified = response.split()
        # an example: 'last-modified': '20121128150000'
        lastmodified = int(time.mktime(datetime.strptime(lastmodified, '%Y%m%d%H%M%S').timetuple()))
        return lastmodified

    def get_file_list(self):
        genome_li = [x for x in self.client.nlst() if not x.endswith('.')]
        fli = []
        fixed_files = ['../hg38/database/refFlat.txt.gz',
                       '../mm9/database/refFlat.txt.gz',
                       '../hgFixed/database/refLink.txt.gz']
        for file_path in [os.path.join(genome, "database/refFlat.txt.gz") for genome in genome_li] + fixed_files:
            lastmodified = self.get_ftpfile_lastmodified(file_path)
            if lastmodified:
                fli.append((file_path,lastmodified))
            else:
                # file probably doesn't exist (no refflat)
                pass
        self.latest_lastmodified = sorted([x[1] for x in fli])[-1]
        return fli

    def remote_is_better(self,remote_info,localfile):
        remotefile, remote_lastmodified = remote_info
        res = os.stat(localfile)
        local_lastmodified = int(res.st_mtime)
        if remote_lastmodified > local_lastmodified:
            self.logger.debug("Remote file '%s' is newer (remote: %s, local: %s)" %
                    (remotefile,remote_lastmodified,local_lastmodified))
            return True
        self.logger.debug("'%s' is up-to-date, no need to download" % remotefile)
        return False

    def create_todump_list(self, force=False):
        self.to_dump = []
        remote_files = self.get_file_list()
        for remote_file, remote_lastmodified in remote_files:
            localfile = os.path.join(self.current_data_folder, self.CWD_DIR, remote_file)
            if force or not os.path.exists(localfile) or \
                    self.remote_is_better((remote_file, remote_lastmodified), localfile):
                # register new release (will be stored in backend)
                self.release = self.timestamp
                self.to_dump.append({"remote": remote_file,"local":localfile})

