import os.path
from utils.dataload import (load_start, load_done, tab2dict)
from config import DATA_ARCHIVE_ROOT
DATA_FOLDER = os.path.join(DATA_ARCHIVE_ROOT,'by_resources/reporters')
platform_li = ['GNF1H', 'GNF1M']

def loaddata():
    #GNF1H
    DATAFILE = os.path.join(DATA_FOLDER, 'gnf', 'GNF1H.ANNO7.LOAD_20130402.tab')
    load_start(DATAFILE)
    gene2gnf1h = tab2dict(DATAFILE, (0, 5), 1,header=0,includefn=lambda ld:len(ld)>5 and ld[5]!='')
    load_done('[%d]' % len(gene2gnf1h))
    #GNF1m
    DATAFILE = os.path.join(DATA_FOLDER, 'gnf', 'gnf1m.NEW_ANNO6.LOAD_20130402.tab')
    load_start(DATAFILE)
    gene2gnf1m = tab2dict(DATAFILE, (0, 5), 1,header=0,includefn=lambda ld:len(ld)>5 and ld[5]!='')
    load_done('[%d]' % len(gene2gnf1m))

    return {'GNF1H': gene2gnf1h,
            'GNF1M': gene2gnf1m}

