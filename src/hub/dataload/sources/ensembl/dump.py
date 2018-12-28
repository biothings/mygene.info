import sys
import os
import time
from ftplib import FTP
import requests

import biothings, config
biothings.config_for_app(config)

from biothings.utils.common import timesofar, safewfile, is_int
from biothings.utils.hipchat import hipchat_msg
from biothings.utils.hub_db import get_src_dump
from biothings.utils.dataload import tab2list
from config import DATA_ARCHIVE_ROOT, logger as logging
from biothings.hub.dataload.dumper import HTTPDumper, DumperException


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
    pass

class BioMart(HTTPDumper):

    # actual biotmart url to use (webservice)
    MART_URL = None

    # list of species to download data for.
    # will be set by implementing select_species()
    species_li = []

    # dict of {filename:method} with filename is the remote file to 
    # dump and method is a BioMart method implemented in subclass, which
    # define which fields to get from biotmart
    DUMP_METHOD = {}

    # xml query template, must be defined in subclass
    TEMPLATE = None

    def download(self,remotefile,localfile):
        self.prepare_local_folders(localfile)
        self.logger.debug("Downloading '%s'" % os.path.basename(localfile))
        # remote is a method name
        method = getattr(self,remotefile)
        method(localfile)
        # rough sanity check against "empty" files w/ just headers
        if os.stat(localfile).st_size < 1024*1024: # at least 1MiB
            raise DumperException("'%s' is too small, no data ?" % localfile)

    def new_release_available(self):
        current_release = self.src_doc.get("download",{}).get("release")
        if not current_release or self.release > current_release:
            self.logger.info("New release '%s' found" % self.release)
            return True
        else:
            self.logger.debug("No new release found")
            return False

    def create_todump_list(self,force=False):
        self.get_newest_info()
        newrelease = self.new_release_available()
        for fn in self.__class__.DUMP_METHOD:
            local_file = os.path.join(self.new_data_folder,os.path.basename(fn))
            if force or not os.path.exists(local_file) or newrelease:
                if not self.__class__.species_li:
                    self.__class__.species_li = self.select_species()
                method = self.__class__.DUMP_METHOD[fn]
                self.to_dump.append({"remote":method,"local":local_file})

    def get_newest_info(self):
        self.release = self.get_latest_mart_version()

    def _query(self, *args, **kwargs):
        req = requests.Request(*args, **kwargs)
        res = self.client.send(req.prepare())
        if res.status_code != 200:
            raise MartException(res)
        if res.text.startswith('Query ERROR:'):
            raise MartException(res.text)
        return res.text

    def _make_query_xml(self, dataset, attributes, filters=None):
        attrib_xml = '\n'.join(['<Attribute name = "%s" />' % attrib for attrib in attributes])
        if filters:
            filter_xml = '\n'.join(['<Filter name = "%s" excluded = "0"/>' % filter for filter in filters])
        else:
            filter_xml = ''
        return self.__class__.TEMPLATE % {'virtual_schema': self.get_virtual_schema(),
                                     'dataset': dataset,
                                     'attributes': attrib_xml,
                                     'filters': filter_xml}

    def query_mart(self, xml):
        return self._query('POST', self.__class__.MART_URL, data='query=%s\n' % xml)

    def get_registry(self):
        return self._query('GET', self.__class__.MART_URL + '?type=registry')

    def get_datasets(self):
        con = self._query('GET', self.__class__.MART_URL + '?type=datasets&mart=ensembl')
        out = []
        for line in con.split('\n'):
            line = line.strip()
            if line != '':
                ld = line.split('\t')
                out.append((ld[1], ld[2], ld[4]))
        return out

    def _fetch_data(self, outfile, attributes, filters='', header=None, debug=False, setname=''):
        cnt_lines_all = 0
        cnt_species_success = 0
        out_f, outfile = safewfile(outfile,prompt=False,default='O')
        if header:
            out_f.write('\t'.join(header) + '\n')
        for species in self.__class__.species_li:
            try:
                dataset = self.get_dataset_name(species)
            except IndexError:
                # bad dataset name, skip (this used to be catched in a try/finally
                # so it wasn't dealth with before)
                self.logger.debug("Skip species '%s'" % species)
                continue
            taxid = species[2]
            if not dataset:
                continue
            xml = self._make_query_xml(dataset, attributes=attributes, filters=filters)
            if debug:
                self.logger.info(xml)
            try:
                con = self.query_mart(xml)
            except MartException as e:
                import traceback
                # err_msg = traceback.format_exc()
                # self.logger.warn("%s %s %s" % (species[0], attrset, err_msg))
                self.logger.warn("%s %s %s" % (setname, species[0], e))
                continue
            cnt_lines = 0
            # if len(con) == 0 it's not right
            for line in con.split('\n'):
                if line.strip() != '':
                    out_f.write(str(taxid) + '\t' + line + '\n')
                    cnt_lines += 1
                    cnt_lines_all += 1
            self.logger.info("%s %s %d" % (setname, species[0], cnt_lines))
        out_f.close()
        self.logger.info("Total: %s %d/%d %d" % (setname, cnt_species_success, len(self.__class__.species_li), cnt_lines_all))


    def get_latest_mart_version(self):
        raise NotImplementedError("Implement me in sub-class")

    def select_species(self):
        """
        Return a list of tuple containing species to download data for.
        [(species_name1, common_name1, taxid1),(species_name2, common_name2, taxid2), ...]
        """
        raise NotImplementedError("Implement me in sub-class")

    def get_virtual_schema(self):
        """
        Return BioMart schema for this dumper (eg. 'plants_mart', 'default',...)
        """
        raise NotImplementedError("Implement me in sub-class")

    def get_dataset_name(self, species):
        """Given a species tuple(name,taxid) return the dataset name
        for that species in BiotMart"""
        raise NotImplementedError("Implement me in sub-class")

    def get_species_file(self):
        """TODO"""
        raise NotImplementedError("Implement me in sub-class")

class GenericBioMart(BioMart):

    TEMPLATE = XML_QUERY_TEMPLATE
    DUMP_METHOD = {"gene_ensembl__gene__main.txt":"get_gene__main",
                 "gene_ensembl__translation__main.txt":"get_translation__main",
                 "gene_ensembl__xref_entrezgene__dm.txt":"get_xref_entrezgene",
                 "gene_ensembl__prot_profile__dm.txt":"get_profile",
                 "gene_ensembl__prot_interpro__dm.txt":"get_interpro",
                 "gene_ensembl__prot_pfam__dm.txt":"get_pfam"}

    SCHEDULE = "0 6 * * *"

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
        'dbprimary_id':"entrezgene",                    #                           x
        'profile_id':"pfscan",                          #                                     x
        'interpro_id':"interpro",                       #                                              x
        'pfam':"pfam"                                   #                                                    x
    }

    # dump methods implementation for each input files
    def get_gene__main(self, outfile, debug=False):
        header = ['taxonomy_id',
                  'ensembl_gene_id',
                  'symbol',
                  'gene_chrom_start', 'gene_chrom_end', 'chr_name', 'chrom_strand',
                  'description','type_of_gene']
        attributes = self._get_attributes(header)
        self._fetch_data(outfile, attributes, header=header, debug=debug, setname='gene_main')

    def get_translation__main(self, outfile, debug=False):
        header = ['taxonomy_id',
                  'gene_stable_id',
                  'transcript_stable_id',
                  'translation_stable_id']
        attributes = self._get_attributes(header)
        self._fetch_data(outfile, attributes, header=header, debug=debug, setname='translation_main')

    def get_xref_entrezgene(self, outfile, debug=False):
        header = ['taxonomy_id',
                  'gene_stable_id',
                  'dbprimary_id']
        attributes = ["ensembl_gene_id",
                      "entrezgene"]
        filters = ["with_entrezgene"]
        attributes = self._get_attributes(header)
        self._fetch_data(outfile, attributes, filters, header=header, debug=debug, setname='xref_entrezgene')

    def get_profile(self, outfile, debug=False):
        header = ['taxonomy_id',
                  'gene_stable_id',
                  'transcript_stable_id',
                  'translation_stable_id',
                  'profile_id']
        filters = ["with_pfscan"]
        attributes = self._get_attributes(header)
        self._fetch_data(outfile, attributes, filters, header=header, debug=debug, setname='profile')

    def get_interpro(self, outfile, debug=False):
        header = ['taxonomy_id',
                  'gene_stable_id',
                  'transcript_stable_id',
                  'translation_stable_id',
                  'interpro_id']
        attributes = self._get_attributes(header)
        header_additional = ['short_description', 'description']
        attributes_additional = ["interpro_short_description", "interpro_description"]
        header.extend(header_additional)
        attributes.extend(attributes_additional)
        filters = ["with_interpro"]
        self._fetch_data(outfile, attributes, filters, header=header, debug=debug, setname='interpro')

    def get_pfam(self, outfile, debug=False):
        header = ['taxonomy_id',
                  'gene_stable_id',
                  'transcript_stable_id',
                  'translation_stable_id',
                  'pfam']
        attributes = self._get_attributes(header)
        filters = ["with_pfam"]
        self._fetch_data(outfile, attributes, filters, header=header, debug=debug, setname='pfam')

    def _get_attributes(self, header):
        attr = []
        assert header[0] == 'taxonomy_id'
        self.logger.debug(header)
        for h in header[1:]:
            attr.append(self.BIOMART_ATTRIBUTES[h])
        self.logger.debug(attr)
        return attr

class EnsemblBioMart(GenericBioMart):

    SRC_NAME = "ensembl"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    # used to get latest release number & list of available species
    ENSEMBL_FTP_HOST = "ftp.ensembl.org"
    MART_URL = "http://www.ensembl.org/biomart/martservice"

    # overide
    def get_latest_mart_version(self):
        ftp = FTP(self.__class__.ENSEMBL_FTP_HOST)
        ftp.login()
        #release_li = ftp.nlst('/pub/release-*')
        release_li = [x for x in ftp.nlst('/pub') if x.startswith('/pub/release-')]
        return str(sorted([int(fn.split('-')[-1]) for fn in release_li])[-1])

    # overide
    def select_species(self):
        import tempfile
        outfile = tempfile.mktemp() + '.txt.gz'
        try:
            self.logger.info('Downloading Species List...')
            self.logger.debug(self.get_species_file())
            out_f = open(outfile, 'wb')
            ftp = FTP(self.__class__.ENSEMBL_FTP_HOST)
            ftp.login()
            species_file = self.get_species_file()
            ftp.retrbinary("RETR " + species_file, out_f.write)
            out_f.close()
            self.logger.info('Done.')

            #load saved file
            self.logger.info('Loading Species List...')
            species_li = self._load_species(outfile)
            self.logger.info('Done.')
        finally:
            os.remove(outfile)
            pass

        import pprint
        self.logger.debug(pprint.pformat(species_li))
        return species_li
    
    def get_species_file(self):
        return '/pub/release-%s/mysql/ensembl_production_%s/species.txt.gz' % (self.release, self.release)

    def _load_species(self, outfile):
        species_li = tab2list(outfile, (1, 2, 7), header=0)   # db_name,common_name,taxid
        species_li = [x[:-1] + [is_int(x[-1]) and int(x[-1]) or None] for x in species_li]
        # as of ensembl 87, there are also mouse strains. keep only the "original" one
        species_li = [s for s in species_li if not s[0].startswith("mus_musculus_")]
        # species_li = _load_species_extra_processing(species_li)
        return species_li

    # overide
    def get_virtual_schema(self):
        return 'default'

    def _get_species_table_prefix(self, species):
        x = species.split('_')
        return x[0][0] + x[1]

    # overide
    def get_dataset_name(self, species):
        return '%s_gene_ensembl' % self._get_species_table_prefix(species[0])
