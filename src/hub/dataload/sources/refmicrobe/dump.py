import os

import config
from biothings.hub.dataload.dumper import DumperException, LastModifiedHTTPDumper
from biothings.utils.common import dump


class RefMicrobeTaxIDsDumper(LastModifiedHTTPDumper):
    """
    Builds the list of bacterial taxids the entrez_genomic_pos uploader uses to pick
    which microbial genes get genomic_pos from gene2refseq: the taxids of RefSeq
    "reference genome" assemblies in NCBI's bacterial assembly summary.
    """

    SRC_NAME = "ref_microbe_taxids"
    SRC_ROOT_FOLDER = os.path.join(config.DATA_ARCHIVE_ROOT, SRC_NAME)
    SRC_URLS = ["https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/assembly_summary.txt"]
    SCHEDULE = "0 20 * * 6"  # before entrez's weekly dump, so its uploaders get a fresh list
    ARCHIVE = False  # NCBI updates this ~240MB file daily, only keep the latest
    AUTO_UPLOAD = False  # only data is needed

    def post_dump(self, *args, **kwargs):
        summary_file = os.path.join(self.new_data_folder, "assembly_summary.txt")
        taxids = get_ref_microbe_taxids(summary_file)
        if not taxids:
            raise DumperException("No reference genome taxids found in '%s'" % summary_file)
        self.logger.info("Found %s reference genome taxids in '%s'" % (len(taxids), summary_file))
        # loaded by the entrez_genomic_pos uploader
        dump(taxids, os.path.join(self.new_data_folder, "ref_microbe_taxids.pyobj"))


def get_ref_microbe_taxids(assembly_summary_file):
    """
    Return the sorted taxids of "reference genome" assemblies listed in an NCBI
    assembly_summary.txt file. NCBI no longer designates "representative genome"
    assemblies, so "reference genome" is the only category left to select.
    """
    taxids = set()
    with open(assembly_summary_file) as summary:
        for line in summary:
            if line.startswith("#"):
                # the last comment line holds the column names
                header = line.lstrip("#").rstrip("\n").split("\t")
                continue
            row = dict(zip(header, line.rstrip("\n").split("\t")))
            if row.get("refseq_category") == "reference genome":
                taxids.add(row["taxid"])
    return sorted(taxids)
