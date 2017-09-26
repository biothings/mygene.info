import os.path
from biothings.utils.dataload import tab2dict

platform_li = ['snowball']


def loaddata(data_folder):
    #Snowball array
    datafile = os.path.join(data_folder, 'pigatlas', 'snowball_array_annotation.txt')
    gene2snowball = tab2dict(datafile, (0, 1), 1, header=0)
    return {'snowball': gene2snowball}
