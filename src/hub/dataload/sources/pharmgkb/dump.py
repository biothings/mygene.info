

import os, sys, time, datetime

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import LastModifiedHTTPDumper
from biothings.utils.common import unzipall


class PharmgkbDumper(LastModifiedHTTPDumper):

    SRC_NAME = "pharmgkb"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    # URL is always the same, but headers change
    SRC_URLS = ["https://s3.pgkb.org/data/genes.zip"]
    SCHEDULE = "0 6 * * *"

    def post_dump(self, *args, **kwargs):
        self.logger.info("Uncompressing files in '%s'" % self.new_data_folder) 
        unzipall(self.new_data_folder)


