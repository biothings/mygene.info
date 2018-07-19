from biothings.utils.dataload import open_anyfile


def load_data(input_file):

    with open_anyfile(input_file) as in_f:
        for line in in_f:
            pharos_id, _id = line.strip().split(',')
            if _id != 'entrez_gene_id':
                yield {
                    '_id': int(_id),
                    'pharos' : {"target_id" : int(pharos_id)},
                }


