import csv, os
from biothings_client import get_client
from collections import defaultdict

GENE_CLIENT = get_client('gene')


def query_hgnc(hgnc_ids: list):
    """Use biothings_client.py to query hgnc ids and get back '_id' in mygene.info

    :param: hgnc_ids: list of HGNC ids
    """
    res = GENE_CLIENT.querymany(hgnc_ids, scopes='HGNC', fields='_id', returnall=True)
    new_res = defaultdict(list)
    for item in res['out']:
        if not "notfound" in item:
            new_res[item['query']].append(item['_id'])
    return [new_res, res['missing']]


def parse_family(data_folder):
    """ Parses the family.csv into a dictionary

        :return: A dictionary of family_ids that contains hgnc_genegroup information
    """

    family = {}
    infile = os.path.join(data_folder, "family.csv")
    assert os.path.exists(infile)
    with open(infile, encoding='utf-8') as hgnc_family:
        family_reader = csv.DictReader(hgnc_family, delimiter=",")
        for row in family_reader:
            # replace null values
            row = {k: ('' if v == 'NULL' else v) for k, v in row.items()}
            family[row['id']] = {
                "id": row['id'],
                "abbr": row['abbreviation'],
                "name": row['name'],
                "comments": row['external_note'],
                "pubmed": list(map(int, row['pubmed_ids'].split(","))) if row['pubmed_ids'] else [],
                "typical_gene": row['typical_gene']
            }
    return family


def load_family(data_folder):

    # contains the json object
    # key hgnc_id
    hgnc = {}
    family = parse_family(data_folder)
    infile = os.path.join(data_folder, "gene_has_family.csv")
    assert os.path.exists(infile)
    with open(infile, encoding='utf-8') as hgnc_id:
        hgnc_reader = csv.DictReader(hgnc_id, delimiter=",")
        for row in hgnc_reader:
            gene_id = row['hgnc_id']
            family_id = row['family_id']
            # if id exists then add another entry into hgnc_genegroup else make a new json rec
            if gene_id in hgnc.keys():
                hgnc[gene_id]["hgnc_genegroup"].append(family[family_id])
            else:
                hgnc[gene_id] = {
                    "_id": gene_id,
                    "hgnc_genegroup": [family[family_id]]
                }

    query = query_hgnc(list(hgnc.keys()))
    for key in query[1]:
        hgnc.pop(key, None)
    print(len(hgnc.keys()))
    for key, value in query[0].items():
        hgnc[key]["_id"] = value[0]
        yield hgnc[key]
