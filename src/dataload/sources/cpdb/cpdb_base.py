import os.path
import time

from utils.common import get_timestamp, timesofar
from utils.dataload import (load_start, load_done, tabfile_feeder,
                            list2dict, value_convert, dict_convert)
from dataload import get_data_folder

DATA_FOLDER = get_data_folder('cpdb')


def _download(__metadata__):
    from utils.dataload import download as _download

    output_folder = os.path.join(os.path.split(DATA_FOLDER)[0], get_timestamp())
    for species in ['human', 'mouse', 'yeast']:
        url = __metadata__['__url_{}__'.format(species)]
        output_file = 'CPDB_pathways_genes_{}.tab'.format(species)
        _download(url, output_folder, output_file)


def load_cpdb(__metadata__):
    # only import pathways from these sources
    PATHWAY_SOURCES_INCLUDED = __metadata__['pathway_sources_included']
    VALID_COLUMN_NO = 4

    t0 = time.time()
    print('DATA_FOLDER: ' + DATA_FOLDER)
    DATA_FILES = []
    DATA_FILES.append(os.path.join(DATA_FOLDER, 'CPDB_pathways_genes_mouse.tab'))
    DATA_FILES.append(os.path.join(DATA_FOLDER, 'CPDB_pathways_genes_yeast.tab'))
    DATA_FILES.append(os.path.join(DATA_FOLDER, 'CPDB_pathways_genes_human.tab'))

    _out = []
    for DATA_FILE in DATA_FILES:
        load_start(DATA_FILE)
        for ld in tabfile_feeder(DATA_FILE, header=1, assert_column_no=VALID_COLUMN_NO):
            p_name, p_id, p_source = ld[:3]
            p_source = p_source.lower()
            if p_source == 'kegg' and p_id.startswith('path:'):
                p_id = p_id[5:]
            if p_source in PATHWAY_SOURCES_INCLUDED:
                genes = ld[-1].split(",")
                for gene in genes:
                    _out.append((gene, p_name, p_id, p_source))
        load_done()
    _out = list2dict(_out, 0, alwayslist=True)

    def _inner_cvt(p):
        p_name, p_id = p
        _d = {'name': p_name}
        if p_id != 'None':
            _d['id'] = p_id
        return _d

    def _cvt(pli):
        _d = list2dict(pli, 2)
        _d = value_convert(_d, _inner_cvt)
        for p_source in _d:
            if isinstance(_d[p_source], list):
                _d[p_source].sort()
        return {'pathway': _d}

    _out = dict_convert(_out, valuefn=_cvt)
    load_done('[%d, %s]' % (len(_out), timesofar(t0)))

    return _out
