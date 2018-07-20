import os
from config import DATA_ARCHIVE_ROOT, logger as logging
from hub.dataload.sources.ensembl.dump import BioMart, XML_QUERY_TEMPLATE

class EnsemblPlantBioMart(BioMart):

    SRC_NAME = "ensembl_plant"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    # used to get latest release number & list of available species
    ENSEMBL_FTP_HOST = "ftp.ensembl.org"
    MART_URL = "https://plants.ensembl.org/biomart/martservice"
    #MART_URL = "http://uswest.ensembl.org/biomart/martservice"
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
        #release_li = ftp.nlst('/pub/release-*')
        release_li = [x for x in ftp.nlst('/pub') if x.startswith('/pub/release-')]
        return str(sorted([int(fn.split('-')[-1]) for fn in release_li])[-1])

    def select_species(self):
        import tempfile
        outfile = tempfile.mktemp() + '.txt.gz'
        try:
            self.logger.info('Downloading "species.txt.gz"...')
            out_f = open(outfile, 'wb')
            ftp = FTP(self.__class__.ENSEMBL_FTP_HOST)
            ftp.login()
            species_file = '/pub/release-%s/mysql/ensembl_production_%s/species.txt.gz' % (self.release, self.release)
            ftp.retrbinary("RETR " + species_file, out_f.write)
            out_f.close()
            self.logger.info('Done.')

            #load saved file
            self.logger.info('Parsing "species.txt.gz"...')
            species_li = tab2list(outfile, (1, 2, 7), header=0)   # db_name,common_name,taxid
            species_li = [x[:-1] + [is_int(x[-1]) and int(x[-1]) or None] for x in species_li]
            # as of ensembl 87, there are also mouse strains. keep only the "original" one
            species_li = [s for s in species_li if not s[0].startswith("mus_musculus_")]
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
        x = species.split('_')
        return x[0][0] + x[1]

    def get_dataset_name(self, species):
        return '%s_eg_gene' % self._get_species_table_prefix(species[0])

    # dump methods implementation for each input files
    def get_gene__main(self, outfile, debug=False):
        header = ['taxonomy_id',
                  'ensembl_gene_id',
                  'symbol',
                  'gene_chrom_start', 'gene_chrom_end', 'chr_name', 'chrom_strand',
                  'description','type_of_gene']
        attributes = ["ensembl_gene_id",
                      "external_gene_name",   # symbols, called "external_gene_id" before release 76
                      "start_position", "end_position", "chromosome_name", "strand",
                      "description","gene_biotype"]
        self._fetch_data(outfile, attributes, header=header, debug=debug)


Plant_Query_trial = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Query>
<Query  virtualSchemaName = "plants_mart" formatter = "TSV" header = "0" uniqueRows = "0" count = "" datasetConfigVersion = "0.6" >
			
	<Dataset name = "athaliana_eg_gene" interface = "default" >
		<Filter name = "biotype" value = "antisense_RNA"/>
		<Attribute name = "ensembl_gene_id" />
		<Attribute name = "start_position" />
		<Attribute name = "end_position" />
		<Attribute name = "external_gene_name" />
		<Attribute name = "chromosome_name" />
		<Attribute name = "strand" />
		<Attribute name = "description" />
		<Attribute name = "gene_biotype" />
	</Dataset>
</Query>
'''


