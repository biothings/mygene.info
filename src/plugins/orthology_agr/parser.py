"""
# Orthology AGR Data Parser  
# Organization: Su and Wu labs @ Scripps Research  
# Data parser for the Alliance of Genome Resources database for ortholog relationships. 
"""
# load packages
import os
from biothings_client import get_client
import biothings.utils.dataload as dl
import time
import logging
import json


logging = logging.getLogger("orthology_agr")

def setup_release(self):
    release="2019-06-23"
    return release


def convert_score(score):
    """
        Converts the isbestscore and isbestrevscore 
        from a string to boolean. 
        score: "Yes" or "No" string 
    """
    if score=="Yes":
        return True;
    else:
        return False;

def adjust_gene_ids(gene_id_list):
    # Adjust prefixes directly in the list
    adjustments = {
        "WB:": "WormBase:",
        "FB:": "FLYBASE:",
        "XB": "XenBase:XB",
    }

    for i, gene_id in enumerate(gene_id_list):
        for prefix, replacement in adjustments.items():
            if gene_id.startswith(prefix):
                gene_id_list[i] = gene_id.replace(prefix, replacement)
                break
    
    return gene_id_list


def get_gene_cache(unique_gene_ids, gene_client, batch_size=1000):
    gene_id_cache = {}
    first_pass_fail_ct = 0
    error_ids = []

    # Convert set to list for manipulation
    unique_gene_ids=adjust_gene_ids(list(unique_gene_ids))
    # Convert back to set if you need to remove duplicates after adjustment
    unique_gene_ids = set(unique_gene_ids)

    def batch(iterable, n=1):
        """Yield successive n-sized batches from iterable."""
        # Convert set to list if iterable is a set
        if isinstance(iterable, set):
            iterable = list(iterable)
        
        l = len(iterable)
        for ndx in range(0, l, n):
            yield iterable[ndx:min(ndx + n, l)]

    # Iterate through batches and perform query
    for batch_ids in batch(unique_gene_ids, batch_size):
        try: 
            results = gene_client.querymany(
                batch_ids,
                scopes=["WormBase", "MGI", "FLYBASE", "Xenbase", "WB"],
                fields='symbol,name,entrezgene',
                verbose=False
            )
            for result in results:
                query_id = result['query']
                if 'notfound' in result:
                    first_pass_fail_ct += 1
                    # Second pass query -- attempt to get Entrez ID directly
                    try:
                        query_res = gene_client.query(query_id, fields='entrezgene')
                        if query_res.get('hits'):
                            for hit in query_res['hits']:
                                if 'entrezgene' in hit:
                                    gene_id_cache[query_id] = hit['entrezgene']
                        else:
                            logging.info(f"query ID not found in second individual query: {query_id}")
                            error_ids.append(query_id)
                    except Exception as e:
                        logging.error(f"Error in second pass query for {query_id}: {e}")
                else:
                    # Process found queries
                    # original_gene_id = result.get('_id')
                    entrez_id = result.get('entrezgene')
                    # if original_gene_id and entrez_id:
                    if entrez_id:
                        gene_id_cache[query_id] = entrez_id
                    else:
                        logging.info(f"Missing data for found query: {result.get('query', 'Unknown ID')}")
        except Exception as e:
            logging.error(f"Error in batch query: {e}")

    logging.info("Completed building gene ID cache.")
    logging.info(f"First pass fail count: {first_pass_fail_ct}")
    logging.info(f"Final error IDs (complete fail): {len(error_ids)}")

    return gene_id_cache

def load_orthology(data_folder):
    """Main method for parsing ortholog data from AGR."""
    start_time = time.time()

    infile = os.path.join(data_folder, "ORTHOLOGY-ALLIANCE_COMBINED.tsv.gz")
    logging.info(f"Starting upload for orthology AGR from {infile}")
    assert os.path.exists(infile), "Input file does not exist."

    gene_client = get_client('gene')
    unique_gene_ids = set() 

    # Collect unique gene IDs
    line_count = 0
    for line in dl.tabfile_feeder(infile, header=1, sep="\t"):
        # if sample_limit and line_count >= sample_limit:
        #     break
        if len(line) >= 5:
            unique_gene_ids.update([line[0], line[4]])
            line_count += 1

    # Fetch gene IDs in parallel -- use batch with querymany
    gene_id_cache = get_gene_cache(unique_gene_ids, gene_client)

    # Construct records using fetched gene IDs
    records = {}
    line_count = 0
    for line in dl.tabfile_feeder(infile, header=1, sep="\t"):
        # if sample_limit and line_count >= sample_limit:
        #     break
        if len(line) < 5:
            continue
        gene_id, ortholog_id = gene_id_cache.get(line[0]), gene_id_cache.get(line[4])
        if gene_id and ortholog_id:
            # Create a record if gene_id not in records, or append ortholog if gene_id already exists
            if gene_id not in records:
                records[gene_id] = {
                    "_id": gene_id,
                    "orthologs": []
                }
            ortholog_record = {
                "gene_id": gene_id,
                "ortholog_id": ortholog_id,
                "symbol": line[5],
                "taxid": int(float(line[6].split(":")[1])),
                "algorithmsmatch": line[9],
                "outofalgorithms": line[10],
                "isbestscore": convert_score(line[11]),
                "isbestrevscore": convert_score(line[12])
            }
            records[gene_id]["orthologs"].append(ortholog_record)
            line_count += 1  # Increment the line counter

    elapsed_time = time.time() - start_time
    logging.info(f"Completed processing {sum(len(rec['orthologs']) for rec in records.values())} ortholog records for {len(records)} genes in {elapsed_time:.2f} seconds.")
    if records:
        logging.info(f"Sample record: {json.dumps(records[next(iter(records))], indent=2)}")

    return list(records.values())
