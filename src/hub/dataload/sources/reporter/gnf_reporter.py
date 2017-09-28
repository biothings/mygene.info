import os.path
from biothings.utils.dataload import tab2dict

platform_li = ['GNF1H', 'GNF1M']

def loaddata(data_folder):
    #GNF1H
    datafile = os.path.join(data_folder, 'gnf', 'GNF1H.ANNO7.LOAD_20130402.tab')
    gene2gnf1h = tab2dict(datafile, (0, 5), 1, header=0, includefn=lambda ld: len(ld) > 5 and ld[5] != '')
    #GNF1m
    datafile = os.path.join(data_folder, 'gnf', 'gnf1m.NEW_ANNO6.LOAD_20130402.tab')
    gene2gnf1m = tab2dict(datafile, (0, 5), 1, header=0, includefn=lambda ld: len(ld) > 5 and ld[5] != '')

    return {'GNF1H': gene2gnf1h,
            'GNF1M': gene2gnf1m}
