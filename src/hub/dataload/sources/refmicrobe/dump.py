import os
import os.path
import sys
import time
from datetime import datetime

import config
from biothings.hub.dataload.dumper import LastModifiedHTTPDumper


class RefMicrobeTaxIDsDumper(LastModifiedHTTPDumper):

    SRC_NAME = "ref_microbe_taxids"
    SRC_ROOT_FOLDER = os.path.join(config.DATA_ARCHIVE_ROOT, SRC_NAME)
    SRC_URLS = ["http://biothings-data.s3-website-us-west-2.amazonaws.com/mygene.info/ref_microbe_taxids.pyobj"]
    AUTO_UPLOAD = False # only data is needed

