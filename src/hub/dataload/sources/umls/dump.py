import datetime
import os

import bs4
import dateutil.parser as dtparser
from biothings.hub.dataload.dumper import DumperException, HTTPDumper
from biothings.utils.common import unzipall

from config import DATA_ARCHIVE_ROOT


class UMLSDumper(HTTPDumper):

    SRC_NAME = "umls"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    SCHEDULE = "0 12 * * *"
    HOMEPAGE_URL = "https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html"

    def get_latest_release(self):
        res = self.client.get(self.__class__.HOMEPAGE_URL)
        # Raise error if status is not 200
        res.raise_for_status()
        html = bs4.BeautifulSoup(res.text, "lxml")
        # Get the table of metathesaurus release files
        table = html.find("table", attrs={"class": "usa-table margin-bottom-4"})
        rows = table.find_all("tr")
        # The header of the fifth column should be 'Date'
        assert (
            rows[0].find_all("th")[4].text.strip() == "Date"
        ), "Could not parse version from html table."
        version = rows[1].find_all("td")[4].text
        try:
            latest = datetime.date.strftime(dtparser.parse(version), "%Y-%m-%d")
            return latest
        except Exception as e:
            raise DumperException(
                "Can't find or parse date from table field {}: {}" % (version, e)
            )

    def create_todump_list(self, force=True):
        self.release = self.get_latest_release()
        if (
            force
            or not self.src_doc
            or (
                self.src_doc
                and self.src_doc.get("download", {}).get("release") < self.release
            )
        ):
            self.logger.info(
                "Manually download from: https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html"
            )
            # Create data folder
            local = os.path.join(self.SRC_ROOT_FOLDER, self.release)
            if not os.path.exists(local):
                os.makedirs(local)
            # Dump a dummy file, to mark dump as successful and trigger uploader
            release_notes = "https://www.nlm.nih.gov/research/umls/knowledge_sources/metathesaurus/release/notes.html"
            self.to_dump.append(
                {
                    "remote": release_notes,
                    "local": os.path.join(local, "release_notes.html"),
                }
            )

    def post_dump(self, *args, **kwargs):
        self.logger.info("Unzipping files in '%s'" % self.new_data_folder)
        unzipall(self.new_data_folder)
