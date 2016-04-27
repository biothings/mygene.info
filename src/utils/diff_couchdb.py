import types
def _clean_acc(acc):
    out = {}
    for attr in ['genomic', 'protein', 'rna']:
        if attr in acc:
            v = acc[attr]
            if type(v) is types.ListType:
                out[attr] = [x.split('.')[0] for x in v]
            else:
                out[attr] = v.split('.')[0]
    return out


def diff_doc1(doc_1, doc_2):
    diff_d = {'update': {},
              'delete': [],
              'add': {}}
    for attr in set(doc_1) | set(doc_2):
        if attr in ['_rev', 'pir', 'Vega']:
            continue
        if attr in doc_1 and attr in doc_2:
            _v1 = doc_1[attr]
            _v2 = doc_2[attr]

            if attr == 'MGI':
                _v2 = _v2.split(':')[1]
            elif attr in ['refseq', 'accession']:
                _v1 = _clean_acc(_v1)
            elif attr == 'interpro':
                if type(_v1) is types.ListType:
                    _v1.sort()
                if type(_v2) is types.ListType:
                    _v2.sort()
            elif attr == 'reagent':
                for k in _v1.keys():
                    if k.find('.') != -1:
                        _v1[k.replace('.', '_')] = _v1[k]
                        del _v1[k]



            if _v1 != _v2:
                diff_d['update'][attr] = _v2
        elif attr in doc_1 and attr not in doc_2:
            diff_d['delete'].append(attr)
        else:
            diff_d['add'][attr] = doc_2[attr]
    if diff_d['update'] or diff_d['delete'] or diff_d['add']:
        return diff_d