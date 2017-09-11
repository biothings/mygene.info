import os.path
from utils.dataload import (load_start, load_done, tab2dict, value_convert)
from dataload import get_data_folder
from .umls_parser import load_data

DATA_FOLDER = get_data_folder('umls')


def load_umls():
    print('DATA_FOLDER: ' + DATA_FOLDER)
    DATAFILE = os.path.join(DATA_FOLDER, 'MRCONSO.RRF')
    umls_docs = load_data(DATAFILE)
    return umls_docs
