

import os, sys, time, datetime

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import LastModifiedHTTPDumper
from biothings.utils.common import unzipall


class ReactomeDumper(LastModifiedHTTPDumper):

    SRC_NAME = "reactome"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    # URL is always the same, but headers change
    SRC_URLS = ["https://reactome.org/download/current/NCBI2Reactome_All_Levels.txt"]
    SCHEDULE = "0 6 * * *"

