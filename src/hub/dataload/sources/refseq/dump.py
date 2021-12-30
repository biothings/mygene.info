import os
import os.path
import sys
import time
import glob
import asyncio
from functools import partial
from datetime import datetime

import biothings, config

biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT, logger as logging
from biothings.hub.dataload.dumper import FTPDumper
from biothings.utils.common import dump
from .parse_refseq_gbff import GBFFParser


class RefseqDumper(FTPDumper):
    SRC_NAME = "refseq"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    FTP_HOST = 'ftp.ncbi.nih.gov'
    CWD_DIR = '/refseq'

    SCHEDULE = "0 6 * * *"

    def get_newest_info(self):
        rel = None

        def setrel(line):
            nonlocal rel
            rel = line

        self.client.retrlines("RETR /refseq/release/RELEASE_NUMBER", setrel)
        self.release = rel

    def new_release_available(self):
        current_release = self.src_doc.get("download", {}).get("release")
        if not current_release or self.release > current_release:
            self.logger.info("New release '%s' found" % self.release)
            return True
        else:
            self.logger.debug("No new release found")
            return False

    def create_todump_list(self, force=False):
        self.get_newest_info()
        for wild in ['H_sapiens/mRNA_Prot/human.*.rna.gbff.gz',
                    'M_musculus/mRNA_Prot/mouse.*.rna.gbff.gz',
                    'S_scrofa/mRNA_Prot/pig.*.rna.gbff.gz']:
            files = self.client.nlst(wild)
            for fn in files:
                local_file = os.path.join(self.new_data_folder, os.path.basename(fn))
                if force or not os.path.exists(local_file) or self.remote_is_better(fn,
                                                                                    local_file) or self.new_release_available():
                    self.to_dump.append({"remote": fn, "local": local_file})

    def post_dump(self, job_manager=None, *args, **kwargs):
        # we're in a new thread, we need to "bring back" the loop to run jobs
        # (it's fine, processes we'll use are independent)
        gbff_files = glob.glob(os.path.join(self.new_data_folder, '*.rna.gbff.gz'))
        self.logger.info("Parsing %d refseq gbff files" % len(gbff_files))
        asyncio.set_event_loop(job_manager.loop)
        job = self.parse_gbff(gbff_files, job_manager)
        task = asyncio.ensure_future(job)
        return task

    @asyncio.coroutine
    def parse_gbff(self, gbff_files, job_manager):
        out_d = {}
        jobs = []
        got_error = False
        for infile in gbff_files:
            baseinfile = os.path.basename(infile)
            pinfo = self.get_pinfo()
            pinfo["step"] = "post-dump (gbff)"
            pinfo["description"] = baseinfile
            job = yield from job_manager.defer_to_process(pinfo, partial(parser_worker, infile))

            def parsed(res, fn):
                nonlocal out_d
                try:
                    out_li = res.result()
                    self.logger.info("%d records parsed from %s" % (len(out_li), fn))
                    species = os.path.basename(fn).split('.')[0]
                    out_d.setdefault(species, []).extend(out_li)
                except Exception as e:
                    self.logger.error("Failed parsing gbff file '%s': %s" % (fn, e))
                    nonlocal got_error
                    got_error = e

            job.add_done_callback(partial(parsed, fn=infile))
            jobs.append(job)
            # stop the loop asap if error
            if got_error:
                raise got_error
        if jobs:
            yield from asyncio.gather(*jobs)
            if got_error:
                raise got_error
            # if we get here, result is ready to be dumped
            outfile = os.path.join(self.new_data_folder, 'rna.gbff.parsed.pyobj')
            self.logger.info("Dump gbff parsed data to '%s'" % outfile)
            dump(out_d, outfile, compress="lzma")
            # output gene2summary text file
            self.logger.info("Generate gene2summary")
            sumout = os.path.join(self.new_data_folder, 'gene2summary_all.txt')
            output_gene2summary(out_d, sumout)
            assert os.path.getsize(sumout) > 0
            # output gene2ec text file
            self.logger.info("Generate gene2ec")
            ecout = os.path.join(self.new_data_folder, 'gene2ec_all.txt')
            output_gene2ec(out_d, ecout)
            assert os.path.getsize(ecout) > 0
            # output gene2cds text file
            self.logger.info("Generate gene2cds")
            cdsout = os.path.join(self.new_data_folder, 'gene2cds_all.txt')
            output_gene2cds(out_d, cdsout)
            assert os.path.getsize(cdsout) > 0


def parser_worker(infile):
    gb = GBFFParser(infile)
    return gb.parse()


def output_gene2summary(out_d, outfile):
    '''Output tab delimited file for gene summary, with two column
       gene summary
       (no header line)
    '''
    out_f = open(outfile, 'w')
    for species in out_d:
        out_li = []
        for rec in out_d[species]:
            geneid = rec[0]
            summary = rec[1]
            if summary:
                out_li.append((geneid, summary))

        for geneid, summary in sorted(set(out_li)):
            out_f.write('%s\t%s\n' % (geneid, summary))
    out_f.close()


def output_gene2ec(out_d, outfile):
    '''Output tab delimited file for gene EC numbers, with two column
       gene ec_number
       (multiple ec_numbers are comma-seperated)
       (no header line)
    '''
    out_f = open(outfile, 'w')
    for species in out_d:
        dd = {}
        for rec in out_d[species]:
            geneid = rec[0]
            ec_list = rec[2]
            if ec_list:
                if geneid in dd:
                    dd[geneid].extend(ec_list)
                else:
                    dd[geneid] = ec_list
        for geneid in sorted(dd.keys()):
            out_f.write('%s\t%s\n' % (geneid,
                                      ','.join(sorted(set(dd[geneid])))))
    out_f.close()


def output_gene2cds(out_d, outfile):
    '''Output tab delimited file for ccds, with 4 columns (geneid, ccds, location, refseq)
       (no header line)
    '''
    out_f = open(outfile, 'w')
    for species in out_d:
        out_li = []
        for rec in out_d[species]:
            geneid = rec[0]
            ccds = rec[3]
            location = rec[4]
            refseq = rec[5]
            if ccds:
                out_li.append((geneid, ccds, location, refseq))

        for geneid, ccds, location, refseq in sorted(set(out_li)):
            out_f.write('%s\t%s\t%s\t%s\n' % (geneid, ccds, location, refseq))
    out_f.close()

