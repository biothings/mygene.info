import os.path
from biothings.utils.dataload import tab2dict, value_convert

def load_pharmgkb(data_folder):
    datafile = os.path.join(data_folder, 'genes.zip')
    gene2pharmgkb = tab2dict((datafile, 'genes.tsv'), (0, 1), 1, header=1, includefn=lambda ld: ld[1] != '')
    fn = lambda value: {'pharmgkb': value}
    gene2pharmgkb = value_convert(gene2pharmgkb, fn, traverse_list=False)
    return gene2pharmgkb
