import os, sys, time, datetime
import bs4

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import HTTPDumper
from biothings.utils.common import unzipall


class CPDBDumper(HTTPDumper):

    SRC_NAME = "cpdb"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    HOME_PAGE = "http://cpdb.molgen.mpg.de/CPDB/rlFrame"
    URLS = {"human" : "http://cpdb.molgen.mpg.de/CPDB/getPathwayGenes?idtype=entrez-gene",
            "mouse" : "http://cpdb.molgen.mpg.de/MCPDB/getPathwayGenes?idtype=entrez-gene",
            "yeast" : "http://cpdb.molgen.mpg.de/YCPDB/getPathwayGenes?idtype=entrez-gene"}
    SCHEDULE = "0 6 * * *"

    def get_remote_version(self):
        home = self.client.get(self.__class__.HOME_PAGE)
        bs = bs4.BeautifulSoup(home.text,"html.parser")
        # first span is the date besides release number
        date = bs.find("span")
        rel_num_date = date.parent.text.split()
        assert len(rel_num_date) == 3, "Unable to parser release from line: '%s':" % date.parent.text
        assert rel_num_date[0] == "Release", "First element should be 'Release': %s" % rel_num_date
        # release number
        return rel_num_date[1]

    def create_todump_list(self, force=False):
        self.release = self.get_remote_version()
        if force or not self.current_release or int(self.release) > int(self.current_release):
            for species in self.__class__.URLS:
                remote_file = self.__class__.URLS[species]
                local_file = os.path.join(self.new_data_folder,"CPDB_pathways_genes_%s.tab" % species)
                self.to_dump.append({"remote":remote_file,"local":local_file})

