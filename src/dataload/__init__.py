import time, datetime, types, copy
import importlib

from pymongo.errors import DuplicateKeyError, BulkWriteError

import biothings.dataload.uploader as uploader
from biothings.utils.mongo import get_src_conn, get_src_dump
from biothings.utils.common import get_timestamp, get_random_string, timesofar, dump2gridfs, iter_n


__sources_dict__ = [
    {'entrez': [
        'dataload.sources.entrez.entrez_gene',
        'dataload.sources.entrez.entrez_homologene',
        'dataload.sources.entrez.entrez_genesummary',
        'dataload.sources.entrez.entrez_accession',
        'dataload.sources.entrez.entrez_refseq',
        'dataload.sources.entrez.entrez_unigene',
        'dataload.sources.entrez.entrez_go',
        'dataload.sources.entrez.entrez_ec',
        'dataload.sources.entrez.entrez_retired',
        'dataload.sources.entrez.entrez_generif',
        'dataload.sources.entrez.entrez_genomic_pos',
    ]},
    {'ensembl': [
        'dataload.sources.ensembl.ensembl_gene',
        'dataload.sources.ensembl.ensembl_acc',
        'dataload.sources.ensembl.ensembl_genomic_pos',
        'dataload.sources.ensembl.ensembl_prosite',
        'dataload.sources.ensembl.ensembl_interpro',
        'dataload.sources.ensembl.ensembl_pfam'
    ]},
    {'uniprot': [
        'dataload.sources.uniprot',
        'dataload.sources.uniprot.uniprot_pdb',
        # 'dataload.sources.uniprot.uniprot_ipi',   # IPI is now discontinued, last update is still in the db, but won't be updated.
        'dataload.sources.uniprot.uniprot_pir'
    ]},
    'dataload.sources.pharmgkb',
    'dataload.sources.reporter',
    'dataload.sources.ucsc.ucsc_exons',
    'dataload.sources.exac.broadinstitute_exac',
    'dataload.sources.cpdb',
    'dataload.sources.reagent',
]


