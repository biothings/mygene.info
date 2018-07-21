import os, sys, time, datetime

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import LastModifiedHTTPDumper


class PharosDumper(LastModifiedHTTPDumper):

    SRC_NAME = "pharos"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    SRC_URLS = ["http://sulab-dev.scripps.edu/kevin/pharos/target/pharos_target_mapping.csv"]
    SCHEDULE = "0 3 * * *"
