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

from __future__ import print_function
import sys
import os
import os.path
import time
from datetime import datetime
from urllib2 import urlparse
from ftplib import FTP, error_perm
src_path = os.path.split(os.path.split(os.path.split(os.path.abspath(__file__))[0])[0])[0]
sys.path.append(src_path)
from utils.common import safewfile, LogPrint, timesofar
from utils.mongo import get_src_dump
from config import DATA_ARCHIVE_ROOT

timestamp = time.strftime('%Y%m%d')
# DATA_FOLDER=os.path.join(DATA_ARCHIVE_ROOT, 'by_resources/ucsc', timestamp)
DATA_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, 'by_resources/ucsc')

FTP_SERVER = 'hgdownload.cse.ucsc.edu'
BASE_PATH = 'goldenPath/currentGenomes'
# DATAFILE_PATH = 'pub/databases/uniprot/current_release/knowledgebase/idmapping/idmapping_selected.tab.gz'

latest_lastmodified = None   # a global variable to record the lastmodified for the newest file.


def get_ftpfile_lastmodified(ftp, file_path):
    '''return lastmodified for a given file on ftp server.'''
    try:
        response = ftp.sendcmd('MDTM ' + file_path)
    except error_perm:
        return None
    code, lastmodified = response.split()
    # an example: 'last-modified': '20121128150000'
    lastmodified = datetime.strptime(lastmodified, '%Y%m%d%H%M%S')
    return lastmodified


def get_file_list():
    ftp = FTP(FTP_SERVER)
    ftp.login()
    genome_li = [x for x in ftp.nlst('goldenPath/currentGenomes') if not x.endswith('.')]
    fli = []
    for genome in genome_li:
        for f in ['database/refFlat.txt.gz']:
            file_path = os.path.join(genome, f)
            fli.append(file_path)
    # now add refFlat.txt.gz for hg38
    file_path = 'goldenPath/hg38/database/refFlat.txt.gz'
    fli.append(file_path)
    # now add refFlat.txt.gz for mm9
    file_path = 'goldenPath/mm9/database/refFlat.txt.gz'
    fli.append(file_path)

    fli = [(file_path, get_ftpfile_lastmodified(ftp, file_path)) for file_path in fli]
    fli = [x for x in fli if x[1]]    # remove item if lastmodified is None
    ftp.close()

    if fli:
        global latest_lastmodified
        latest_lastmodified = sorted([x[1] for x in fli])[-1]

    return fli


def get_file_list_for_download():
    refflat_file_list = get_file_list()
    download_list = []
    for file_path, lastmodified in refflat_file_list:
        local_file = os.path.join(DATA_FOLDER, file_path)
        if not os.path.exists(local_file) or \
            (time.mktime(lastmodified.timetuple()) > os.stat(local_file)[-2]):
            download_list.append(file_path)
            download_list.append(file_path.replace('refFlat', 'refLink'))
    return download_list


def download_ftp_file(url, outfile):
    url_parsed = urlparse.urlparse(url)
    assert url_parsed.scheme == 'ftp'
    ftp = FTP(url_parsed.hostname)
    ftp.login()
    with file(outfile, 'wb') as out_f:
        ftp.retrbinary('RETR %s' % url_parsed.path, out_f.write)

    # set the mtime to match remote ftp server
    response = ftp.sendcmd('MDTM ' + url_parsed.path)
    code, lastmodified = response.split()
    # an example: 'last-modified': '20121128150000'
    lastmodified = time.mktime(datetime.strptime(lastmodified, '%Y%m%d%H%M%S').timetuple())
    os.utime(outfile, (lastmodified, lastmodified))


def download(download_list=None, no_confirm=False):
    orig_path = os.getcwd()
    try:
        os.chdir(DATA_FOLDER)
        download_list = download_list or get_file_list_for_download()
        if download_list:
            for file_path in download_list:
                os.chdir(DATA_FOLDER)
                path = os.path.split(file_path)[0]
                if not os.path.exists(path):
                    os.makedirs(path)
                os.chdir(path)
                print('Downloading "%s"...' % file_path, end='')
                url = 'ftp://{}/{}'.format(FTP_SERVER, file_path)
                download_ftp_file(url, os.path.join(DATA_FOLDER, file_path))
                print("done.")
                #cmdline = 'wget -N %s' % url
                ##cmdline = 'axel -a -n 5 %s' % url   #faster than wget using 5 connections
                #return_code = os.system(cmdline)
                #if return_code == 0:
                #    print "Success."
                #else:
                #    print cmdline
                #    print "Failed with return code (%s)." % return_code
                print("="*50)
            return len(download_list)
        else:
            return 0
    finally:
        os.chdir(orig_path)


if __name__ == '__main__':
    no_confirm = True   # set it to True for running this script automatically without intervention.

    src_dump = get_src_dump()
    download_list = get_file_list_for_download()
    if len(download_list) == 0:
        print("No newer file found. Abort now.")
        sys.exit(0)

    doc = src_dump.find_one({'_id': 'ucsc'})
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

    log_f, logfile = safewfile(os.path.join(DATA_FOLDER, 'ucsc_dump.log'), prompt=(not no_confirm), default='O')
    sys.stdout = LogPrint(log_f, timestamp=True)

    # mark the download starts
    doc = {'_id': 'ucsc',
           'timestamp': timestamp,
           'data_folder': DATA_FOLDER,
           'lastmodified': latest_lastmodified,
           'logfile': logfile,
           'status': 'downloading'}
    src_dump.save(doc)
    t0 = time.time()
    try:
        download(download_list, no_confirm)
    finally:
        sys.stdout.close()
    # mark the download finished successfully
    _updates = {
        'status': 'success',
        'time': timesofar(t0),
        'pending_to_upload': True    # a flag to trigger data uploading
    }
    src_dump.update({'_id': 'ucsc'}, {'$set': _updates})
