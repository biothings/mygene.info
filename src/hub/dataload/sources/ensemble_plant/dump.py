import os
from ftplib import FTP
from config import DATA_ARCHIVE_ROOT, logger as logging
from biothings.utils.dataload import tab2list
from biothings.utils.common import is_int
from hub.dataload.sources.ensembl.dump import GenericBioMart, XML_QUERY_TEMPLATE

class EnsemblPlantBioMart(GenericBioMart):

    SRC_NAME = "ensembl_plant"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    # used to get latest release number & list of available species
    ENSEMBL_FTP_HOST = "ftp.ensemblgenomes.org"
    MART_URL = "http://plants.ensembl.org/biomart/martservice"
    TEMPLATE = XML_QUERY_TEMPLATE
    DUMP_METHOD = {"gene_ensembl__gene__main.txt":"get_gene__main",
                 "gene_ensembl__translation__main.txt":"get_translation__main",
                 "gene_ensembl__xref_entrezgene__dm.txt":"get_xref_entrezgene",
                 "gene_ensembl__prot_profile__dm.txt":"get_profile",
                 "gene_ensembl__prot_interpro__dm.txt":"get_interpro",
                 "gene_ensembl__prot_pfam__dm.txt":"get_pfam"}

    SCHEDULE = "0 6 * * *"

    def get_latest_mart_version(self):
        ftp = FTP(self.__class__.ENSEMBL_FTP_HOST)
        ftp.login()
        release_li = [x for x in ftp.nlst('/pub/plants') if x.startswith('/pub/plants/release-')]
        return str(sorted([int(fn.split('-')[-1]) for fn in release_li])[-1])

    def select_species(self):
        import tempfile
        outfile = tempfile.mktemp() + '.txt.gz'
        try:
            self.logger.info('Downloading "dataset_names.txt.gz"...')
            out_f = open(outfile, 'wb')
            ftp = FTP(self.__class__.ENSEMBL_FTP_HOST)
            ftp.login()
            species_file = '/pub/plants/release-%s/mysql/plants_mart_%s/dataset_names.txt.gz' % (self.release, self.release)
            ftp.retrbinary("RETR " + species_file, out_f.write)
            out_f.close()
            self.logger.info('Done.')

            #load saved file
            self.logger.info('Parsing "dataset_names.txt.gz"...')
            species_li = tab2list(outfile, (0, 4, 5), header=0)
            species_li = [[x[0]] + [x[2]] + [x[1]] for x in species_li]
            species_li = [x[:-1] + [is_int(x[-1]) and int(x[-1]) or None] for x in species_li]
            self.logger.info('Done.')
        finally:
            os.remove(outfile)
            pass

        import pprint
        self.logger.error(pprint.pformat(species_li))
        return species_li


    def get_virtual_schema(self):
        return 'plants_mart'

    def _get_species_table_prefix(self, species):
        return species
        
    def get_dataset_name(self, species):
        return '%s_gene' % self._get_species_table_prefix(species[0])
