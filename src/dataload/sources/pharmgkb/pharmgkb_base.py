import os.path
from utils.dataload import (load_start, load_done, tab2dict, value_convert)
from biothings.utils.mongo import get_data_folder
#from config import DATA_ARCHIVE_ROOT

#timestamp = '20121005'
#DATA_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, 'by_resources/pharmgkb', timestamp)
DATA_FOLDER = get_data_folder('pharmgkb')


def load_pharmgkb():
    print('DATA_FOLDER: ' + DATA_FOLDER)
    DATAFILE = os.path.join(DATA_FOLDER, 'genes.zip')
    load_start(DATAFILE)
    gene2pharmgkb = tab2dict((DATAFILE, 'genes.tsv'), (0, 1), 1, header=1, includefn=lambda ld: ld[1] != '')
    fn = lambda value: {'pharmgkb': value}
    gene2pharmgkb = value_convert(gene2pharmgkb, fn, traverse_list=False)

    load_done('[%d]' % len(gene2pharmgkb))

    return gene2pharmgkb
