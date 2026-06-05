import os
import re
from urllib.parse import urljoin

import biothings
import config

biothings.config_for_app(config)

from biothings.hub.dataload.dumper import LastModifiedHTTPDumper, DumperException
from config import DATA_ARCHIVE_ROOT


class PharosDumper(LastModifiedHTTPDumper):

    SRC_NAME = "pharos"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    # The TDL file is versioned and its name changes between releases
    # (e.g. pharos400_tdls_full.csv), so we scrape the directory listing to
    # find the current "*tdls_full.csv" file and build SRC_URLS from it.
    LISTING_URL = "https://opendata.ncats.nih.gov/public/pharos/"
    SRC_URLS = []  # resolved dynamically in create_todump_list()
    SCHEDULE = "0 6 * * *"

    def create_todump_list(self, force=False, **kwargs):
        res = self.client.get(self.__class__.LISTING_URL)
        res.raise_for_status()
        # find the file ending in tdls_full.csv in the directory listing
        matches = re.findall(r'href="([^"]*tdls_full\.csv)"', res.text)
        if not matches:
            raise DumperException(
                "Could not find a '*tdls_full.csv' file at %s" % self.__class__.LISTING_URL
            )
        filename = os.path.basename(matches[-1])
        self.__class__.SRC_URLS = [urljoin(self.__class__.LISTING_URL, filename)]
        super().create_todump_list(force=force)
