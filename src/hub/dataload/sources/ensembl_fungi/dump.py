import os
from ftplib import FTP

from biothings.utils.common import is_int
from biothings.utils.dataload import tab2list
from config import DATA_ARCHIVE_ROOT, logger as logging
from hub.dataload.sources.ensembl.dump import XML_QUERY_TEMPLATE, GenericBioMart


class EnsemblFungiBioMart(GenericBioMart):

    SRC_NAME = "ensembl_fungi"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    # used to get latest release number & list of available species
    ENSEMBL_FTP_HOST = "ftp.ensemblgenomes.org"
    MART_URL = "http://fungi.ensembl.org/biomart/martservice"

    RELEASE_FOLDER = '/pub/fungi'
    RELEASE_PREFIX = '/pub/fungi/release-'

    def get_species_file(self):
        return '/pub/fungi/release-%s/mysql/fungi_mart_%s/dataset_names.txt.gz' % (self.release, self.release)

    def get_virtual_schema(self):
        return 'fungi_mart'

    def get_check_file_path(self):
        return self.get_species_file()
