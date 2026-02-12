import os
from ftplib import FTP

from biothings.utils.common import is_int
from biothings.utils.dataload import tab2list
from config import DATA_ARCHIVE_ROOT, logger as logging
from hub.dataload.sources.ensembl.dump import XML_QUERY_TEMPLATE, GenericBioMart


class EnsemblMetazoaBioMart(GenericBioMart):

    SRC_NAME = "ensembl_metazoa"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    # used to get latest release number & list of available species
    ENSEMBL_FTP_HOST = "ftp.ensemblgenomes.org"
    MART_URL = "http://metazoa.ensembl.org/biomart/martservice"

    RELEASE_FOLDER = '/pub/metazoa'
    RELEASE_PREFIX = '/pub/metazoa/release-'

    def get_species_file(self):
        return '/pub/metazoa/release-%s/mysql/metazoa_mart_%s/dataset_names.txt.gz' % (self.release, self.release)

    def get_virtual_schema(self):
        return 'metazoa_mart'

    def get_check_file_path(self):
        return self.get_species_file()
