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
from ftplib import FTP

import biothings, config
biothings.config_for_app(config)

from biothings.utils.common import ask, timesofar, safewfile, setup_logfile
from biothings.utils.hipchat import hipchat_msg
from biothings.utils.mongo import get_src_dump
from config import DATA_ARCHIVE_ROOT, logger as logging


timestamp = time.strftime('%Y%m%d')
DATA_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, 'exac', timestamp)

FTP_SERVER = 'ftp.broadinstitute.org'
DATAFILES_PATH = [
        'pub/ExAC_release/current/functional_gene_constraint/fordist_cleaned_exac_nonTCGA_z_pli_rec_null_data.txt',
        'pub/ExAC_release/current/functional_gene_constraint/fordist_cleaned_exac_r03_march16_z_pli_rec_null_data.txt',
        'pub/ExAC_release/current/functional_gene_constraint/fordist_cleaned_nonpsych_z_pli_rec_null_data.txt'
        ]


def download(no_confirm=False):
    orig_path = os.getcwd()
    try:
        os.chdir(DATA_FOLDER)
        for one_file in DATAFILES_PATH:
            path, filename = os.path.split(one_file)
            if os.path.exists(filename):
                if no_confirm or ask('Remove existing file "%s"?' % filename) == 'Y':
                    os.remove(filename)
                else:
                    logging.info("Skipped!")
                    return
            logging.info('Downloading "%s"...' % filename)
            url = 'ftp://{}/{}'.format(FTP_SERVER, one_file)
            cmdline = 'wget %s -O %s' % (url, filename)
            #cmdline = 'axel -a -n 5 %s' % url   #faster than wget using 5 connections
            return_code = os.system(cmdline)
            if return_code == 0:
                logging.info("Success.")
            else:
                logging.info("Failed with return code (%s)." % return_code)
            logging.info("=" * 50)
    finally:
        os.chdir(orig_path)


def check_lastmodified():
    ftp = FTP(FTP_SERVER)
    ftp.login()
    # check one, expect all changing at the same time
    response = ftp.sendcmd('MDTM ' + DATAFILES_PATH[0])
    code, lastmodified = response.split()
    assert code == '213', "Error: fail to access data file."
    # an example: 'last-modified': '20121128150000'
    lastmodified = datetime.strptime(lastmodified, '%Y%m%d%H%M%S')
    return lastmodified


def main(no_confirm=True):

    src_dump = get_src_dump()
    lastmodified = check_lastmodified()
    doc = src_dump.find_one({'_id': 'exac'})
    if doc and 'lastmodified' in doc and lastmodified <= doc['lastmodified']:
        path, filename = os.path.split(DATAFILES_PATH[0])
        data_file = os.path.join(doc['data_folder'], filename)
        if os.path.exists(data_file):
            logging.info("No newer file found. Abort now.")
            sys.exit(0)

    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    else:
        if not (no_confirm or len(os.listdir(DATA_FOLDER)) == 0 or ask('DATA_FOLDER (%s) is not empty. Continue?' % DATA_FOLDER) == 'Y'):
            sys.exit(0)

    logfile = os.path.join(DATA_FOLDER, 'exac_dump.log')
    setup_logfile(logfile)

    #mark the download starts
    doc = {'_id': 'exac',
           'timestamp': timestamp,
           'data_folder': DATA_FOLDER,
           'lastmodified': lastmodified,
           'logfile': logfile,
           'status': 'downloading'}
    src_dump.save(doc)
    t0 = time.time()
    download(no_confirm)
    #mark the download finished successfully
    _updates = {
        'status': 'success',
        'time': timesofar(t0),
        'pending_to_upload': True    # a flag to trigger data uploading
    }
    src_dump.update({'_id': 'exac'}, {'$set': _updates})

if __name__ == '__main__':
    try:
        main()
        hipchat_msg('"exac" downloader finished successfully',color='green')
    except Exception as e:
        import traceback
        logging.error("Error while downloading: %s" % traceback.format_exc())
        hipchat_msg('"exac" downloader failed: %s' % e,color='red')
        sys.exit(255)

