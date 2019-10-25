''' Generic BioMart Dumper And Ensembl (Vertebrate) BioMart Dumper '''
import os
from ftplib import FTP

import requests

import config
from biothings import config_for_app
from biothings.hub.dataload.dumper import DumperException, HTTPDumper
from biothings.utils.common import is_int, safewfile
from biothings.utils.dataload import tab2list

config_for_app(config)


XML_QUERY_TEMPLATE_EXAMPLE = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Query>
<Query  virtualSchemaName = "default" formatter = "TSV" header = "0" uniqueRows = "1" count = "" datasetConfigVersion = "0.6" >

    <Dataset name = "hsapiens_gene_ensembl" interface = "default" >
        <Attribute name = "ensembl_gene_id" />
        <Attribute name = "ensembl_transcript_id" />
        <Attribute name = "ensembl_peptide_id" />
    </Dataset>
</Query>
'''

XML_QUERY_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Query>
<Query  virtualSchemaName = "%(virtual_schema)s" formatter = "TSV" header = "0" uniqueRows = "1" count = "" datasetConfigVersion = "0.6" >
    <Dataset name = "%(dataset)s" interface = "default" >
        %(filters)s
        %(attributes)s
    </Dataset>
</Query>
'''


class MartException(Exception):
    ''' Generic BioMart Exception '''


class EntrezgeneNotFound(MartException):
    ''' BioMart complains no entrezgene id entry for the given specie '''


class GeneNameNotFound(MartException):
    ''' BioMart complains no external_gene_name (symbol) for the given specie '''


class GenericBioMart(HTTPDumper):
    '''Generic BioMart Dumper for all Ensembl Sources'''
    # actual biotmart url to use (webservice)
    MART_URL = None

    # dict of {filename:method} with filename is the remote file to
    # dump and method is a BioMart method implemented in subclass, which
    # define which fields to get from biotmart
    DUMP_METHOD = {"gene_ensembl__gene__main.txt": "_get_gene__main",
                   "gene_ensembl__translation__main.txt": "_get_translation__main",
                   "gene_ensembl__xref_entrezgene__dm.txt": "_get_xref_entrezgene",
                   "gene_ensembl__prot_profile__dm.txt": "_get_profile",
                   "gene_ensembl__prot_interpro__dm.txt": "_get_interpro",
                   "gene_ensembl__prot_pfam__dm.txt": "_get_pfam"}

    # pylint: disable=line-too-long
    BIOMART_ATTRIBUTES = {                              # gene_main trans_main xref_entrez profile interpro pfam
        'ensembl_gene_id':"ensembl_gene_id",            #     x
        'gene_stable_id':"ensembl_gene_id",             #                x          x         x        x      x
        'symbol':"external_gene_name",                  #     x
        'gene_chrom_start':"start_position",            #     x
        'gene_chrom_end':"end_position",                #     x
        'chr_name':"chromosome_name",                   #     x
        'chrom_strand':"strand",                        #     x
        'description':"description",                    #     x
        'type_of_gene':"gene_biotype",                  #     x
        'transcript_stable_id':"ensembl_transcript_id", #                x                    x        x     x
        'translation_stable_id':"ensembl_peptide_id",   #                x                    x        x     x
        'dbprimary_id':"entrezgene_id",                 #                           x
        'profile_id':"pfscan",                          #                                     x
        'interpro_id':"interpro",                       #                                              x
        'pfam':"pfam"                                   #                                                    x
    }

    # xml query template, must be defined in subclass
    TEMPLATE = XML_QUERY_TEMPLATE

    # override in sub-class
    ENSEMBL_FTP_HOST = ''
    RELEASE_FOLDER = ''
    RELEASE_PREFIX = ''

    SCHEDULE = "0 6 * * *"

    def __init__(self):
        self.species_li = []
        super().__init__()

    # override BaseDumper
    def create_todump_list(self, force=False, **kwargs):
        self.release = self._get_latest_mart_version()
        newrelease = self._new_release_available()
        self.species_li = self._select_species()
        for file_name in self.__class__.DUMP_METHOD:
            local_path = os.path.join(
                self.new_data_folder, os.path.basename(file_name))
            if force or not os.path.exists(local_path) or newrelease:
                method_name = self.__class__.DUMP_METHOD[file_name]
                self.to_dump.append(
                    {"remote": method_name, "local": local_path})

    # helper for self.create_todump_list()
    def _get_latest_mart_version(self):
        ftp = FTP(self.__class__.ENSEMBL_FTP_HOST)
        ftp.login()
        release_li = [x for x in ftp.nlst(
            self.RELEASE_FOLDER) if x.startswith(self.RELEASE_PREFIX)]
        self.logger.debug("release_li = %s", str(release_li))
        return str(sorted([int(fn.split('-')[-1]) for fn in release_li])[-1])

    # helper for self.create_todump_list()
    def _new_release_available(self):
        current_release = self.src_doc.get("download", {}).get("release")
        if not current_release or self.release > current_release:
            self.logger.info("New release '%s' found", self.release)
            return True
        self.logger.debug("No new release found")
        return False

    # helper for self.create_todump_list()
    def _select_species(self):
        """
        Return a list of tuple containing species to download data for.
        [(species_name1, common_name1, taxid1),(species_name2, common_name2, taxid2), ...]
        """
        import tempfile
        outfile = tempfile.mktemp() + '.txt.gz'
        try:
            self.logger.info('Downloading Species List...')
            out_f = open(outfile, 'wb')
            ftp = FTP(self.__class__.ENSEMBL_FTP_HOST)
            ftp.login()
            species_file = self.get_species_file()
            ftp.retrbinary("RETR " + species_file, out_f.write)
            out_f.close()
            self.logger.info('Done.')

            # load saved file
            self.logger.info('Loading Species List...')
            species_li = tab2list(outfile, (0, 4, 5), header=0)
            species_li = [[x[0]] + [x[2]] + [x[1]] for x in species_li]
            species_li = [
                x[:-1] + [is_int(x[-1]) and int(x[-1]) or None] for x in species_li]
            self.logger.info('Done.')
        finally:
            os.remove(outfile)

        import pprint
        self.logger.debug('\n %s', pprint.pformat(species_li))
        return species_li

    # override HTTPDumper(BaseDumper)
    def download(self, remotefile, localfile):  # pylint: disable=arguments-differ
        self.prepare_local_folders(localfile)
        self.logger.debug("Downloading '%s'", os.path.basename(localfile))
        # remote is a method name
        method = getattr(self, remotefile)
        method(localfile)
        # rough sanity check against "empty" files w/ just headers
        if os.stat(localfile).st_size < 1024*1024:  # at least 1MiB
            raise DumperException("'%s' is too small, no data ?" % localfile)

    # called by dump methods
    def _fetch_data(self, outfile, attributes, filters='', header=None):
        cnt_lines_all = 0
        cnt_species_success = 0
        out_f, outfile = safewfile(outfile, prompt=False, default='O')
        if header:
            out_f.write('\t'.join(header) + '\n')
        for count, species in enumerate(self.species_li):
            try:
                dataset = self.get_dataset_name(species)
            except IndexError:
                self.logger.debug("Skip species '%s'", species)
                continue
            if not dataset:
                continue
            taxid = species[2]
            xml = self._make_query_xml(
                dataset, attributes=attributes, filters=filters)
            try:
                con = self.query_mart(xml)
            except EntrezgeneNotFound as err:
                if 'xref_entrezgene' in outfile:
                    cnt_species_success += 1
                    self.logger.warning("%s:: %s: %s", os.path.basename(outfile),
                                        species[0], 'Skipping species without entrez gene id')
                else:
                    self.logger.error("%s:: %s %s", os.path.basename(outfile), species[0], err)
                continue
            except GeneNameNotFound as err:
                _attributes = attributes.copy()
                _attr_ext_gene_index = attributes.index('external_gene_name')
                _attributes.remove('external_gene_name')
                self.logger.debug(_attributes)
                _xml = self._make_query_xml(
                    dataset, attributes=_attributes, filters=filters)
                try:
                    con = self.query_mart(_xml)
                except MartException as err:
                    self.logger.error("%s:: %s %s", os.path.basename(outfile), species[0], err)
                self.logger.warning("%s:: %s: %s", os.path.basename(outfile), species[0],
                                    'Retried to request species without external gene name')
                cnt_lines = 0
                cnt_species_success += 1
                for line in con.split('\n'):
                    if line.strip() != '':
                        tsv = line.split('\t')
                        out_f.write(str(taxid) + '\t' +
                                    tsv[0] + '\t\t' + '\t'.join(tsv[1:]) + '\n')
                        cnt_lines += 1
                        cnt_lines_all += 1
                self.logger.info("%s:: %d/%d %s %d records", os.path.basename(outfile),
                                 count + 1, len(self.species_li), species[0], cnt_lines)
                continue
            except MartException as err:
                self.logger.error("%s:: %s %s", os.path.basename(outfile), species[0], err)
                continue
            cnt_lines = 0
            cnt_species_success += 1
            if not con:
                self.logger.error('Empty Response.')
            for line in con.split('\n'):
                if line.strip() != '':
                    out_f.write(str(taxid) + '\t' + line + '\n')
                    cnt_lines += 1
                    cnt_lines_all += 1
            self.logger.info("%s:: %d/%d %s %d records", os.path.basename(outfile),
                             count + 1, len(self.species_li), species[0], cnt_lines)
        out_f.close()
        self.logger.info("Total: %s:: %d/%d successes %d records", os.path.basename(outfile),
                         cnt_species_success, len(self.species_li), cnt_lines_all)

    # helper method for _fetch_data
    def _make_query_xml(self, dataset, attributes, filters=None):
        attrib_xml = '\n'.join(
            ['<Attribute name = "%s" />' % attrib for attrib in attributes])
        if filters:
            filter_xml = '\n'.join(
                ['<Filter name = "%s" excluded = "0"/>' % filter for filter in filters])
        else:
            filter_xml = ''
        return self.__class__.TEMPLATE % {'virtual_schema': self.get_virtual_schema(),
                                          'dataset': dataset,
                                          'attributes': attrib_xml,
                                          'filters': filter_xml}

    # helper method for the three methods below
    def _query(self, *args, **kwargs):
        req = requests.Request(*args, **kwargs)
        res = self.client.send(req.prepare())
        if res.status_code != 200:
            raise MartException(res)
        elif 'entrezgene NOT FOUND' in res.text:
            raise EntrezgeneNotFound(res.text)
        elif 'external_gene_name NOT FOUND' in res.text:
            raise GeneNameNotFound(res.text)
        elif res.text.startswith('Query ERROR:'):
            raise MartException(res.text)
        return res.text

    def query_mart(self, xml):
        ''' Make a POST request to query BioMart '''
        return self._query('POST', self.__class__.MART_URL, data='query=%s\n' % xml)

    def query_registry(self):
        ''' Request Meta Data - Registry Information '''
        return self._query('GET', self.__class__.MART_URL + '?type=registry')

    def query_datasets(self):
        ''' Request Meta Data - Datasets Available for a Mart '''
        con = self._query('GET', self.__class__.MART_URL +
                          '?type=datasets&mart=ensembl')
        out = []
        for line in con.split('\n'):
            line = line.strip()
            if line != '':
                cols = line.split('\t')
                out.append((cols[1], cols[2], cols[4]))
        return out

    ###################################################
    #          dump methods implementations           #
    ###################################################

    def _get_gene__main(self, outfile):
        header = ['taxonomy_id',
                  'ensembl_gene_id',
                  'symbol',
                  'gene_chrom_start', 'gene_chrom_end', 'chr_name', 'chrom_strand',
                  'description', 'type_of_gene']
        attributes = self._lookup_attributes(header)
        self._fetch_data(outfile, attributes, header=header)

    def _get_translation__main(self, outfile):
        header = ['taxonomy_id',
                  'gene_stable_id',
                  'transcript_stable_id',
                  'translation_stable_id']
        attributes = self._lookup_attributes(header)
        self._fetch_data(outfile, attributes, header=header)

    def _get_xref_entrezgene(self, outfile):
        header = ['taxonomy_id',
                  'gene_stable_id',
                  'dbprimary_id']
        attributes = ["ensembl_gene_id",
                      "entrezgene"]
        filters = ["with_entrezgene"]
        attributes = self._lookup_attributes(header)
        self._fetch_data(outfile, attributes, filters)

    def _get_profile(self, outfile):
        header = ['taxonomy_id',
                  'gene_stable_id',
                  'transcript_stable_id',
                  'translation_stable_id',
                  'profile_id']
        filters = ["with_pfscan"]
        attributes = self._lookup_attributes(header)
        self._fetch_data(outfile, attributes, filters, header=header)

    def _get_interpro(self, outfile):
        header = ['taxonomy_id',
                  'gene_stable_id',
                  'transcript_stable_id',
                  'translation_stable_id',
                  'interpro_id']
        attributes = self._lookup_attributes(header)
        header.extend(['short_description', 'description'])
        attributes.extend(
            ["interpro_short_description", "interpro_description"])
        filters = ["with_interpro"]
        self._fetch_data(outfile, attributes, filters, header=header)

    def _get_pfam(self, outfile):
        header = ['taxonomy_id',
                  'gene_stable_id',
                  'transcript_stable_id',
                  'translation_stable_id',
                  'pfam']
        attributes = self._lookup_attributes(header)
        filters = ["with_pfam"]
        self._fetch_data(outfile, attributes, filters, header=header)

    def _lookup_attributes(self, header):
        attrs = []
        assert header[0] == 'taxonomy_id'
        self.logger.debug(header)
        for attr in header[1:]:
            attrs.append(self.BIOMART_ATTRIBUTES[attr])
        self.logger.debug(attrs)
        return attrs

    def get_dataset_name(self, species):
        """
        Given a species tuple(name,taxid) return the dataset name for that species
        Modified in EnsemblBioMart only
        """
        return '%s_gene' % species[0]

    def get_species_file(self):
        """
        Return species list file URL for this database
        """
        raise NotImplementedError("Implement me in sub-class")

    def get_virtual_schema(self):
        """
        Return BioMart schema for this dumper (eg. 'plants_mart', 'default',...)
        """
        raise NotImplementedError("Implement me in sub-class")


class EnsemblBioMart(GenericBioMart):
    ''' Ensembl (Vertebrate) BioMart HTTP Dumper '''

    SRC_NAME = "ensembl"
    SRC_ROOT_FOLDER = os.path.join(config.DATA_ARCHIVE_ROOT, SRC_NAME)

    # used to get latest release number & list of available species
    ENSEMBL_FTP_HOST = "ftp.ensembl.org"
    MART_URL = "http://uswest.ensembl.org/biomart/martservice"

    RELEASE_FOLDER = '/pub'
    RELEASE_PREFIX = '/pub/release-'

    def get_species_file(self):
        return '/pub/release-%s/mysql/ensembl_mart_%s/dataset_names.txt.gz' \
            % (self.release, self.release)

    def get_virtual_schema(self):
        return 'default'

    def get_dataset_name(self, species):
        return '%s_gene_ensembl' % species[0]
