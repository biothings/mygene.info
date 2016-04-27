import os.path
import time
from utils.common import timesofar
from utils.dataload import (load_start, load_done,
                            listitems, dupline_seperator,
                            tabfile_feeder, list2dict, list_nondup,
                            value_convert)
#from config import DATA_ARCHIVE_ROOT
from dataload import get_data_folder

#DATA_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, 'by_resources/uniprot')
DATA_FOLDER = get_data_folder('uniprot')

#REF:
#ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/README
VALID_COLUMN_NO = 22


def get_uniprot_section(uniprotkb_id):
    '''return either "Swiss-Prot" or "TrEMBL", two sections of UniProtKB,
       based on input uniprotkb_id, or entry name.
       The rule is (http://www.uniprot.org/manual/entry_name):
           Swiss-Prot entries have a maximum of 5 characters before
           the "_", TrEMBL entries have 6 or 10 characters before the "_" (the accession
        some examples:
            TrEMBL: O61847_CAEEL, F0YED1_AURAN, A0A024RB10_HUMAN
            Swiss-Prot: CDK2_HUMAN, CDK2_MOUSE
    '''
    v = uniprotkb_id.split('_')
    if len(v) != 2:
        raise ValueError('Invalid UniprotKB ID')
    #return 'TrEMBL' if len(v[0])==6 else "Swiss-Prot"
    return 'Swiss-Prot' if len(v[0]) <= 5 else "TrEMBL"

def _dict_convert(uniprot_li):
    '''
    convert [(u'E7ESI2', 'TrEMBL'), (u'P24941', 'Swiss-Prot'),
             (u'G3V5T9', 'TrEMBL'), (u'G3V317', 'TrEMBL')] into
    {'Swiss-Prot': u'P24941',
     'TrEMBL': [u'E7ESI2', u'G3V5T9', u'G3V317']}
    '''
    _dict = list2dict(uniprot_li, 1)
    for k, v in _dict.items():
        if isinstance(v, list):
            _dict[k] = sorted(v)
    return {'uniprot': _dict}


def load_uniprot():
    print('DATA_FOLDER: ' + DATA_FOLDER)
    DATAFILE = os.path.join(DATA_FOLDER, 'idmapping_selected.tab.gz')
    load_start(DATAFILE)
    t0 = time.time()
    xli = []
    for ld in tabfile_feeder(DATAFILE, header=1, assert_column_no=VALID_COLUMN_NO):
        ld = listitems(ld, *(0, 1, 2, 18))    # UniProtKB-AC UniProtKB-ID GeneID Ensembl(Gene)
        for value in dupline_seperator(dupline=ld,
                                       dup_idx=[2, 3],   # GeneID and EnsemblID columns may have duplicates
                                       dup_sep='; '):
            value = list(value)
            value[1] = get_uniprot_section(value[1])
            value = tuple(value)
            xli.append(value)

    ensembl2geneid = list2dict([(x[3], x[2]) for x in xli if x[2] != '' and x[3] != ''], 0, alwayslist=True)
    xli2 = []
    for uniprot_acc, section, entrez_id, ensembl_id in xli:
        if entrez_id:
            xli2.append((uniprot_acc, section, entrez_id))
        elif ensembl_id:
            entrez_id = ensembl2geneid.get(ensembl_id, None)
            if entrez_id:
                #if ensembl_id can be mapped to entrez_id
                for _eid in entrez_id:
                    xli2.append((uniprot_acc, section, _eid))
            else:
                #otherwise, just use ensembl_id
                xli2.append((uniprot_acc, section, ensembl_id))

    gene2uniprot = list2dict(list_nondup(xli2), 2, alwayslist=True)
    gene2uniprot = value_convert(gene2uniprot, _dict_convert, traverse_list=False)
    load_done('[%d, %s]' % (len(gene2uniprot), timesofar(t0)))

    return gene2uniprot


def load_x(idx, fieldname, cvt_fn=None):
    '''idx is 0-based column number'''
    print('DATA_FOLDER: ' + DATA_FOLDER)
    DATAFILE = os.path.join(DATA_FOLDER, 'idmapping_selected.tab.gz')
    load_start(DATAFILE)
    t0 = time.time()
    xli = []
    for ld in tabfile_feeder(DATAFILE, header=1, assert_column_no=VALID_COLUMN_NO):
        ld = listitems(ld, *(2, 19, idx))    # GeneID Ensembl(Gene) target_value
        for value in dupline_seperator(dupline=ld,
                                       dup_sep='; '):
            xli.append(value)

    ensembl2geneid = list2dict(list_nondup([(x[1], x[0]) for x in xli if x[0] != '' and x[1] != '']), 0, alwayslist=True)
    xli2 = []
    for entrez_id, ensembl_id, x_value in xli:
        if x_value:
            if cvt_fn:
                x_value = cvt_fn(x_value)
            if entrez_id:
                xli2.append((entrez_id, x_value))
            elif ensembl_id:
                entrez_id = ensembl2geneid.get(ensembl_id, None)
                if entrez_id:
                    for _eid in entrez_id:
                        xli2.append((_eid, x_value))
                else:
                    xli2.append((ensembl_id, x_value))

    gene2x = list2dict(list_nondup(xli2), 0)
    fn = lambda value: {fieldname: sorted(value) if isinstance(value, list) else value}
    gene2x = value_convert(gene2x, fn, traverse_list=False)
    load_done('[%d, %s]' % (len(gene2x), timesofar(t0)))

    return gene2x


def load_pdb():
    fn = lambda pdb_id: pdb_id.split(':')[0]
    return load_x(idx=5, fieldname='pdb', cvt_fn=fn)

# def load_ipi():
#     """IPI is now discontinued.
#        Now removed from idmapping_selected.tab.gz file since 2014/06/11 release.
#     """
#     return load_x(idx=7, fieldname='ipi')

def load_pir():
    return load_x(idx=11, fieldname='pir')
