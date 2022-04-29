from __future__ import print_function
import os.path
from collections import defaultdict
from itertools import chain

from biothings.utils.dataload import tabfile_feeder
from biothings.utils.common import safewfile, anyfile
from biothings.utils.hub_db import get_src_dump


cnt_resolved_multi_mappings = 0
cnt_recovered_missing_mappings = 0


def find_multiple_mappings_from_entrezgene_file(gene_ensembl_entrezgene_dm_file):
    """Input gene_ensembl_entrezgene_dm_file, and identify how many NCBI gene IDs there are for
    each ensembl gene ID. Lines in input file are:

    'gene_ensembl__xref_entrezgene__dm.txt' (useful columns in input_file):

    col1: Ensembl gene ID
    col2: NCBI gene ID

    If there is > 1 NCBI gene ID, we need to process further.
    """
    print("ensembl_ncbi_mapping.py script is running now...")
    print("step 1 start: find where multiple NCBI IDs map to one Ensembl ID")
    ensembl_dict_with_entrez = defaultdict(list)

    with open(gene_ensembl_entrezgene_dm_file) as file_in:
        next(file_in)
        for line in file_in:
            split_line = line.split("\t")
            ensembl_gene_id = split_line[1].strip()
            ncbi_gene_id = split_line[2].strip()
            ensembl_dict_with_entrez[ensembl_gene_id].append(ncbi_gene_id)

    print("number of Ensembl gene IDs mapped to NCBI gene ID: ", len(ensembl_dict_with_entrez))
    multi_mapping_dict = {}
    for key in ensembl_dict_with_entrez:
        if len(ensembl_dict_with_entrez[key]) > 1:
            multi_mapping_dict[key] = ensembl_dict_with_entrez[key]
    print("number of Ensembl IDs with > 1 NCBI gene ID: ", len(multi_mapping_dict))
    print("step 1 end")
    return multi_mapping_dict, len(ensembl_dict_with_entrez)


def create_ensembl_gene_id_dict(gene_ensembl_main_file, multi_mapping_dict):
    """Using gene_ensembl_main_file, identify correct ensembl symbol for each
    ensembl gene ID. Add this information to a new dictionary.

    'gene_ensembl__gene__main.txt' (useful columns in input file):

    col1: Ensembl gene ID
    col2: Ensembl symbol
    """
    print("step 2 start: get Ensembl symbol from Ensembl main file")
    ensembl_dict = defaultdict(list)
    with open(gene_ensembl_main_file) as file_in:
        next(file_in)
        for line in file_in:
            split_line = line.split("\t")
            ensembl_id_from_main = str(split_line[1].strip())
            ensembl_symbol_from_main = split_line[2].strip()

            if ensembl_id_from_main in multi_mapping_dict:
                ensembl_id_dict = {}
                ensembl_id_dict['data'] = {'ncbi_list': multi_mapping_dict[ensembl_id_from_main],
                                           'symbol': ensembl_symbol_from_main,
                                           'gene2ensembl': []}
                ensembl_dict[ensembl_id_from_main] = ensembl_id_dict
    print("step 2 end")
    return ensembl_dict


def find_ncbi_ids_from_gene2ensembl(ensembl_dict, gene2ensembl_file):
    """Input is gene2ensembl_file; maps NCBI gene ID to one Ensembl gene ID.

    'gene2ensembl' (useful columns in input file):

    col1: NCBI gene ID
    col2: Ensembl gene ID
    """
    print("step 3 start: find NCBI IDs from gene2ensembl file")
    file_in = anyfile(gene2ensembl_file)
    #with open(gene2ensembl_file) as file_in:
    try:
        next(file_in)
        for line in file_in:
            split_line = line.split("\t")
            ensembl_gene_id_from_gene2ensembl = split_line[2].strip()
            ncbi_gene_id_from_gene2ensembl = split_line[1].strip()

            if ensembl_gene_id_from_gene2ensembl in ensembl_dict:
                ensembl_dict[ensembl_gene_id_from_gene2ensembl]['data']['gene2ensembl'].append(ncbi_gene_id_from_gene2ensembl)
    finally:
        file_in.close()

    count = 0
    for key in ensembl_dict:
        if len(ensembl_dict[key]['data']['gene2ensembl']) == 1:
            count += 1

    print("Total number of Ensembl gene IDs mapping uniquely with gene2ensembl: ", count)
    print("step 3 end")
    return ensembl_dict, count


def find_ncbi_symbols(gene_info_file,ensembl_dict):
    print("step 4 start: read NCBI gene symbol")
    ncbi_list_to_find = {}
    for key in ensembl_dict:
        ncbi_list = ensembl_dict[key]['data']['ncbi_list']
        for e in ncbi_list:
            ncbi_list_to_find[e] = True
        #gene2ensembl_ncbi_gene_id_match_list = ensembl_dict[key]['data']['gene2ensembl']
        #if len(gene2ensembl_ncbi_gene_id_match_list) != 1:
        #    ncbi_list_to_find.append(ncbi_list)

    for e in list(set([item for sublist in ncbi_list_to_find for item in sublist])):
        ncbi_list_to_find[e] = True

    ncbi_id_symbols = {}
    for ld in tabfile_feeder(gene_info_file):
        if ld[1] in ncbi_list_to_find:
            ncbi_id_symbols[ld[1]] = ld[2]

    print("number of unique NCBI gene IDs to be queried using Entrez gene_info file: ", len(ncbi_list_to_find))
    print("number symbols found in NCBI file: ", len(ncbi_id_symbols))
    print("step 4 end")
    return ncbi_id_symbols


def resolve_multi_mappings_with_gene2ensembl(ensembl_dict, mygene_website_dict, add_source=False):
    """
    Using gene2ensembl file to resolve those 1:m mappings from Ensembl xref file to 1:1 unique mappings:
       - First use gene2ensembl as single match NCBI gene ID (if == 1 match).
       - Next, if no gene2ensembl match, then look at gene_info (Entrez) to find which NCBI
         ID from the NCBI multi mapping list returns the same ensembl symbol as the
         ensembl main file, and use corresponding NCBI gene ID as single match.

    OUTPUT generator:
    ---------------------
    Tuple with ensembl gene ID and NCBI gene ID
    """
    global cnt_resolved_multi_mappings
    cnt_resolved_multi_mappings = 0
    print("step 5 start: Generator-decide whether to use gene2ensembl or symbol for mapping")
    for key in ensembl_dict:
        ncbi_list = ensembl_dict[key]['data']['ncbi_list']
        ensembl_symbol = ensembl_dict[key]['data']['symbol'].upper()
        gene2ensembl_ncbi_gene_id_match_list = ensembl_dict[key]['data']['gene2ensembl']

        if len(gene2ensembl_ncbi_gene_id_match_list) == 1:
            cnt_resolved_multi_mappings += 1
            if add_source is False:
                yield (key, int(gene2ensembl_ncbi_gene_id_match_list[0]))
            else:
                yield (key, int(gene2ensembl_ncbi_gene_id_match_list[0]), '1')

        else:
            ensembl_symbol_list_from_mygene = []
            for ncbi_id in ncbi_list:
                try:
                    ensembl_symbol_list_from_mygene.append(mygene_website_dict[ncbi_id].upper())
                except KeyError:
                    # need this here; keeps list size/order will never match with ensembl_symbol)
                    ensembl_symbol_list_from_mygene.append('symbol_not_found')

            if ensembl_symbol in ensembl_symbol_list_from_mygene:
                if ensembl_symbol_list_from_mygene.count(ensembl_symbol) == 1:
                    ncbi_idx = ensembl_symbol_list_from_mygene.index(ensembl_symbol)
                    cnt_resolved_multi_mappings += 1
                    if add_source is False:
                        yield (key, int(ncbi_list[ncbi_idx]))
                    else:
                        yield (key, int(ncbi_list[ncbi_idx]), '2')

    print("step 5 end")


def get_missing_mappings_from_gene2ensembl(gene_ensembl_entrezgene_dm_file, gene_ensembl_main_file, gene2ensembl_file, add_source=False):
    """Check gene2ensembl file to return those 1:1 ensemblgene-entrezgene mapping missed in Ensembl xref file.
       Note only 1:1 mappings are returned, not those missing but 1:m mappings
       those mappings contains entrezgene ids already mapped to other Ensembl gene ids are also excluded.
       (Basically, those 1:1 mappings from gene2ensembl with no any overlapping with Ensembl xref mappings)
       A generator of (ensemblgene_id, entrezgene_id) is returned
    """
    global cnt_recovered_missing_mappings
    cnt_recovered_missing_mappings = 0

    print("step 6 start: Find missing 1:1 mappings from gene2ensembl")
    # get the existing ensemblgene_to_entregene mappings from Ensembl xref
    ensembl_dict_with_entrez = defaultdict(list)
    with open(gene_ensembl_entrezgene_dm_file) as file_in:
        next(file_in)
        for line in file_in:
            split_line = line.split("\t")
            ensembl_gene_id = split_line[1].strip()
            ncbi_gene_id = split_line[2].strip()
            ensembl_dict_with_entrez[ensembl_gene_id].append(ncbi_gene_id)
    mapped_entrezgene_ids = set()
    for k in ensembl_dict_with_entrez:
        mapped_entrezgene_ids |= set(ensembl_dict_with_entrez[k])

    # get all valid ensembl gene id set
    ensembl_ids = set()
    with open(gene_ensembl_main_file) as file_in:
        next(file_in)
        for line in file_in:
            split_line = line.split("\t")
            ensembl_gene_id = split_line[1].strip()
            ensembl_ids.add(ensembl_gene_id)

    # get missing ensemblgene_to_entrezgene mappings only available from gene2ensembl not from Ensembl xrefs
    ensembl_dict_from_gene2ensembl = defaultdict(list)
    file_in = anyfile(gene2ensembl_file)
    try:
        next(file_in)
        for line in file_in:
            split_line = line.split("\t")
            ensembl_gene_id_from_gene2ensembl = split_line[2].strip()
            ncbi_gene_id_from_gene2ensembl = split_line[1].strip()
            if ensembl_gene_id_from_gene2ensembl in ensembl_ids and ncbi_gene_id_from_gene2ensembl not in mapped_entrezgene_ids and ensembl_gene_id_from_gene2ensembl not in ensembl_dict_with_entrez:
                # only keep those ensembl_gene_ids are valid and have no mapping from Ensembl xrefs
                # also remove only mapping contains entrezgene ids have been mapped to other Ensembl gene ids based on Ensembl xrefs
                ensembl_dict_from_gene2ensembl[ensembl_gene_id_from_gene2ensembl].append(ncbi_gene_id_from_gene2ensembl)
    finally:
        file_in.close()
        del ensembl_dict_with_entrez, mapped_entrezgene_ids, ensembl_ids

    # only keep those 1:1 ensemblgene_to_entrezgene mappings, yield as a generator
    for k, v in ensembl_dict_from_gene2ensembl.items():
        if len(v) == 1:
            cnt_recovered_missing_mappings += 1
            if add_source is False:
                yield (k, int(v[0]))
            else:
                yield (k, int(v[0]), '3')
    print("Total missing 1:1 mappings recovered from gene2ensembl: ", cnt_recovered_missing_mappings)
    print("step 6 end")



def write_mapping_file(mapping_generator, outfile, confirm=True):
    """OUTPUT is mapping file:
    -------------------------
    Note: you will not know the source of the mapping unless you use
    the optional parameter "add_source=True" to merge_mapping() function
    col0: Ensembl gene ID
    col2 "add_source" == 1: NCBI ID gene ID from gene2ensembl
    col2 "add_source" == 2: NCBI ID gene ID from ncbi_list if symbol == ensembl symbol
    col2 "add_source" == 3: NCBI ID gene ID from gene2ensembl which is missing from Ensembl xrefs
        (i.e. iterate through ncbi list (for each Ensembl ID) on gene_info file
        and when the symbol found matches the ensembl symbol use this
        NCBI ID if symbols match only once)
    """
    print("step 7 start: write file from mapping generator of tuples")
    mapping_file, mapping_filename = safewfile(outfile, prompt=confirm,default='O')

    count = 0
    for item in mapping_generator:
        count += 1
        split_item = list(item)
        split_item = '\t'.join([str(i) for i in split_item])
        mapping_file.write(split_item + "\n")

    print("total Ensembl IDs uniquely mapped to NCBI gene ID:", count)
    mapping_file.close()
    print("Output file: \"{}\"".format(mapping_filename))
    print("step 7 end\n")
    return count


def run_stats(total_ensembl_IDs, ensembl_dict, ensembl_map_count, total_mapped):
    print("Final Summary:")
    print("--------------")
    print("# Resolved multiple mappings")
    print("\tTotal Ensembl gene IDs mapped to NCBI gene IDs", total_ensembl_IDs)
    print("\tTotal Ensembl gene IDs with multiple NCBI gene IDs: ", len(ensembl_dict))
    print("\tPercent of Ensembl gene IDs with multiple NCBI gene IDs: ", round((len(ensembl_dict) * 1. / (total_ensembl_IDs)) * 100, 1))
    print("\tTotal Ensembl gene IDs successfully and uniquely mapped to 1 NCBI gene ID: ", cnt_resolved_multi_mappings)
    print("\tTotal mapped using gene2ensembl: ", ensembl_map_count)
    print("\tTotal mapped from symbol: ", cnt_resolved_multi_mappings - ensembl_map_count)
    print("\tPercent of Ensembl IDs uniquely mapped out of Ensembl IDs with > 1 NCBI gene ID: ", round((cnt_resolved_multi_mappings * 1. / (len(ensembl_dict))) * 100, 1))

    print("# Recovered missing mappings")
    print("\tTotal missing 1:1 mappings recovered from gene2ensembl: ", cnt_recovered_missing_mappings)



# def main(gene_ensembl_1, gene_ensembl_2, gene2ensembl):
def main(src_name, confirm=True):
    src_dump = get_src_dump()
    ensembl_doc = src_dump.find_one({"_id":src_name}) or {}
    ENSEMBL_DATA_FOLDER = ensembl_doc.get("download",{}).get("data_folder")
    assert ENSEMBL_DATA_FOLDER, "Can't find Ensembl data folder"
    entrez_doc = src_dump.find_one({"_id":"entrez"}) or {}
    ENTREZ_DATA_FOLDER = entrez_doc.get("download",{}).get("data_folder")
    assert ENTREZ_DATA_FOLDER, "Can't find Entrez data folder"

    gene_ensembl_1_xref_dm_file = os.path.join(ENSEMBL_DATA_FOLDER, "gene_ensembl__xref_entrezgene__dm.txt")
    gene_ensembl_2_main_file = os.path.join(ENSEMBL_DATA_FOLDER, "gene_ensembl__gene__main.txt")
    gene2ensembl_file = os.path.join(ENTREZ_DATA_FOLDER, "gene2ensembl.gz")
    gene_main_file = os.path.join(ENTREZ_DATA_FOLDER, "gene_info.gz")

    outfile = os.path.join(ENSEMBL_DATA_FOLDER, "gene_ensembl__gene__extra.txt")



    multi_mapping_dict, total_ensembl_IDs = find_multiple_mappings_from_entrezgene_file(gene_ensembl_1_xref_dm_file)
    ensembl_dict = create_ensembl_gene_id_dict(gene_ensembl_2_main_file, multi_mapping_dict)
    ensembl_dict, ensembl_match_count = find_ncbi_ids_from_gene2ensembl(ensembl_dict, gene2ensembl_file)
    ncbi_id_symbols = find_ncbi_symbols(gene_main_file, ensembl_dict)
    ##import pickle
    ##pickle.dump(ensembl_dict,open("/tmp/ensembl_dict","wb"))
    ##pickle.dump(ncbi_id_symbols,open("/tmp/ncbi_id_symbols","wb"))
    resolved_multi_mapping_generator = resolve_multi_mappings_with_gene2ensembl(ensembl_dict, ncbi_id_symbols, add_source=False)
    missing_mapping_generator = get_missing_mappings_from_gene2ensembl(gene_ensembl_1_xref_dm_file, gene_ensembl_2_main_file, gene2ensembl_file, add_source=False)
    mapping_generator = chain(resolved_multi_mapping_generator, missing_mapping_generator)
    total_mapped = write_mapping_file(mapping_generator, outfile, confirm=confirm)
    run_stats(total_ensembl_IDs, ensembl_dict, ensembl_match_count, total_mapped)
