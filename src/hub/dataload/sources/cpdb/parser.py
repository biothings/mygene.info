import os.path
import time

from biothings.utils.common import timesofar
from biothings.utils.dataload import tabfile_feeder, list2dict, value_convert, dict_convert


def load_cpdb(data_folder, pathways):
    # only import pathways from these sources
    PATHWAY_SOURCES_INCLUDED = pathways
    VALID_COLUMN_NO = 4

    t0 = time.time()
    DATA_FILES = []
    DATA_FILES.append(os.path.join(data_folder, 'CPDB_pathways_genes_mouse.tab'))
    DATA_FILES.append(os.path.join(data_folder, 'CPDB_pathways_genes_yeast.tab'))
    DATA_FILES.append(os.path.join(data_folder, 'CPDB_pathways_genes_human.tab'))

    _out = []
    for DATA_FILE in DATA_FILES:
        for ld in tabfile_feeder(DATA_FILE, header=1, assert_column_no=VALID_COLUMN_NO):
            p_name, p_id, p_source = ld[:3]
            p_source = p_source.lower()
            if p_source == 'kegg' and p_id.startswith('path:'):
                p_id = p_id[5:]
            if p_source in PATHWAY_SOURCES_INCLUDED:
                genes = ld[-1].split(",")
                for gene in genes:
                    _out.append((gene, p_name, p_id, p_source))
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
                _d[p_source].sort(key=lambda e: e["id"])
        return {'pathway': _d}

    _out = dict_convert(_out, valuefn=_cvt)

    return _out
