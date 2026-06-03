import os

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import LastModifiedHTTPDumper


class PharosDumper(LastModifiedHTTPDumper):

    SRC_NAME = "pharos"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    # URL is always the same, but headers change
    SRC_URLS = ["https://opendata.ncats.nih.gov/public/pharos/current_tdls.csv"]
    SCHEDULE = "0 6 * * *"