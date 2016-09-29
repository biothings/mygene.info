import os.path
from biothings.utils.dataload import (load_start, load_done, tab2dict)

platform_li = ['snowball']


def loaddata(data_folder):
    #Snowball array
    datafile = os.path.join(data_folder, 'pigatlas', 'snowball_array_annotation.txt')
    load_start(datafile)
    gene2snowball = tab2dict(datafile, (0, 1), 1, header=0)
    load_done('[%d]' % len(gene2snowball))
    return {'snowball': gene2snowball}
