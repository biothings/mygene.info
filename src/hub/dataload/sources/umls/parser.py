# Determine UMLS CUI to Entrez Gene id mappings for genes
# 1. Parse UMLS to determine HGNC ids for each CUI
# 2. Use HGNC to convert HGNC ids to Entrez Gene ids
import os
from collections import defaultdict
from biothings_client import get_client

GENE_CLIENT = get_client('gene')

def query_hgnc(hgnc_ids: list) -> dict:
    """Use biothings_client.py to query hgnc ids and get back '_id' in mygene.info
    
    :param: hgnc_ids: list of HGNC ids
    """
    res = GENE_CLIENT.querymany(hgnc_ids, scopes='HGNC', fields='_id')
    new_res = defaultdict(list)
    for item in res:
        if not "notfound" in item:
            new_res[item['query']].append(item['_id'])
    return new_res

def query_uniprot(uniprot_ids: list) -> dict:
    """Use biothings_client.py to query uniprot ids and get back '_id' in mygene.info
    
    :param: uniprot_ids: list of UniProt IDs
    """
    res = GENE_CLIENT.querymany(uniprot_ids, scopes='uniprot.Swiss-Prot', fields='_id')
    new_res = defaultdict(list)
    for item in res:
        if not item.get("notfound"):
            new_res[item['query']].append(item['_id'])
    return new_res

def parse_mrcon(rrf_file):
    """Parse the UMLS to determine the HGNC identifier of each gene CUI.

    The relevant files are in the archive <version>-1-meta.nlm (a zip file)
    within <version>/META/MRCONSO.RRF.*.gz

    Concatenate the unzipped versions of the MRCONSO files together to get the
    final MRCONSO.RRF file, which is a | delimited text file without a header.
    """

    res = defaultdict(set)
    hgnc_ids = set()
    with open(rrf_file, "r") as fin:
        for line in fin:
            if "HGNC:" in line:
                vals = line.rstrip("\n").split("|")

                cui = vals[0]
                for val in vals[1:]:
                    if val.startswith("HGNC:"):
                        res[val.split(':')[-1]].add(cui)
                        hgnc_ids.add(val.split(':')[-1])
    return res, hgnc_ids

def parse_mrsat(rrf_file):
    """Parse the UMLS to determine the UniProt identifier of each protein CUI.

    The relevant file is MRSAT.RRF, which is downloaded from https://download.nlm.nih.gov/umls/kss/2019AB/umls-2019AB-metathesaurus.zip
    """

    res = defaultdict(set)
    uniprot_ids = set()
    with open(rrf_file, "r") as fin:
        for line in fin:
            if "SWISS_PROT" in line:
                vals = line.rstrip("\n").split("|")
                cui = vals[0]
                res[vals[-4]].add(cui)
                uniprot_ids.add(vals[-4])
    return res, uniprot_ids

def unlist(l):
    l = list(l)
    if len(l) == 1:
        return l[0]
    return l

def load_data(data_folder):
    mrsat_file = os.path.join(data_folder, 'MRSAT.RRF')
    mrconso_file = os.path.join(data_folder, 'MRCONSO.RRF') 
    hgnc_map, hgnc_ids = parse_mrcon(mrconso_file)
    uniprot_map, uniprot_ids = parse_mrsat(mrsat_file)
    res = {}
    hgnc2mygeneids = query_hgnc(hgnc_ids)
    uniprot2mygeneids = query_uniprot(uniprot_ids)
    for hgnc, _ids in hgnc2mygeneids.items():
        for _id in _ids:
            res[_id] = {'cui': unlist(hgnc_map[hgnc])}
    for uniprot, _ids in uniprot2mygeneids.items():
        for _id in _ids:
            if _id not in res:
                res[_id] = {}
            res[_id]['protein_cui'] = unlist(uniprot_map[uniprot])
    for _id, item in res.items():
        yield {'_id': _id,
               'umls': item}

