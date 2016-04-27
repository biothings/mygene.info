import os.path
from utils.dataload import (load_start, load_done, tab2dict,
                            dict_apply)
from config import DATA_ARCHIVE_ROOT
DATA_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, 'by_resources/reporters')
AFFY_RELEASE = 'na35'
AFFY_FILE_EXTENSION = '.zip'  # or '.gz'
AFFY_DATA_FOLDER = os.path.join(DATA_FOLDER, 'affy', AFFY_RELEASE)
AFFY_ANNOT_FILES = [
    # human chips
    {'name': 'HG-U133_Plus_2',
     'file': 'HG-U133_Plus_2.%s.annot.csv' + AFFY_FILE_EXTENSION},
    {'name': 'HG-U95Av2',
     'file': 'HG_U95Av2.%s.annot.csv' + AFFY_FILE_EXTENSION},
    {'name': 'HG-U95B',
     'file': 'HG_U95B.%s.annot.csv' + AFFY_FILE_EXTENSION},
    # mouse chips
    {'name': 'Mouse430_2',
     'file': 'Mouse430_2.%s.annot.csv' + AFFY_FILE_EXTENSION},
    {'name': 'MG-U74Av2',
     'file': 'MG_U74Av2.%s.annot.csv' + AFFY_FILE_EXTENSION},
    {'name': 'MG-U74Bv2',
     'file': 'MG_U74Bv2.%s.annot.csv' + AFFY_FILE_EXTENSION},
    # rat chips
    {'name': 'Rat230_2',
     'file': 'Rat230_2.%s.annot.csv' + AFFY_FILE_EXTENSION},
    {'name': 'RG-U34A',
     'file': 'RG_U34A.%s.annot.csv' + AFFY_FILE_EXTENSION},
    {'name': 'RG-U34B',
     'file': 'RG_U34B.%s.annot.csv' + AFFY_FILE_EXTENSION},
    # frog chips
    # {'name': 'X_laevis_2',
    #  'file': 'X_laevis_2.%s.annot.csv' + AFFY_FILE_EXTENSION},
    # {'name': 'X_laevis',
    #  'file': 'Xenopus_laevis.%s.annot.csv' + AFFY_FILE_EXTENSION},
    # {'name': 'X_tropicalis',
    #  'file': 'X_tropicalis.%s.annot.csv' + AFFY_FILE_EXTENSION},

]

platform_li = [af['name'] for af in AFFY_ANNOT_FILES]


def _load_affy(df):
    filename = os.path.split(df)[1]
    rawfile, ext = os.path.splitext(filename)
    if ext.lower() == '.zip':
        df = (df, rawfile)
    dd = tab2dict(df, (0, 18), 1, sep=',', header=1, includefn=lambda ld: len(ld) > 18 and ld[18] != '---' and ld[18] != 'Entrez Gene')
    #fix for keys like "472 /// 4863" for mulitple geneids
    gene2affy = {}
    for k in dd:
        if len(k.split(' /// ')) > 1:
            for kk in k.split(' /// '):
                dict_apply(gene2affy, kk.strip(), dd[k])
        else:
            dict_apply(gene2affy, k.strip(), dd[k])
    return gene2affy


def loaddata():
    affy_d = {}
    for annot in AFFY_ANNOT_FILES:
        name = annot['name']
        DATAFILE = os.path.join(AFFY_DATA_FOLDER, annot['file'] % AFFY_RELEASE)
        load_start(DATAFILE)
        d = _load_affy(DATAFILE)
        affy_d[name] = d
        load_done('[%d]' % len(d))

    return affy_d
