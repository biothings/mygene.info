from biothings.utils.dataload import open_anyfile, unlist
from collections import defaultdict


def load_data(input_file):

    with open_anyfile(input_file) as in_f:
        result = defaultdict(list)
        for line in in_f:
            pharos_id, _id = line.strip().split(',')
            if _id != 'entrez_gene_id' and _id != '0':
                result[str(_id)].append(int(pharos_id))
        for k, v in result.items():
            json_doc = {'_id': str(k),
                        'pharos': {"target_id": v}}
            yield unlist(json_doc)
