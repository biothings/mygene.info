import os.path
from utils.dataload import (load_start, load_done, tab2dict)
from config import DATA_ARCHIVE_ROOT
DATA_FOLDER = os.path.join(DATA_ARCHIVE_ROOT,'by_resources/reporters')
platform_li = ['snowball']

def loaddata():
    #Snowball array
    DATAFILE = os.path.join(DATA_FOLDER, 'pigatlas', 'snowball_array_annotation.txt')
    load_start(DATAFILE)
    gene2snowball = tab2dict(DATAFILE, (0, 1), 1,header=0)
    load_done('[%d]' % len(gene2snowball))
    return {'snowball': gene2snowball}
