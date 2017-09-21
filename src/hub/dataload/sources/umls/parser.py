# Determine UMLS CUI to Entrez Gene id mappings for genes
# 1. Parse UMLS to determine HGNC ids for each CUI
# 2. Use HGNC to convert HGNC ids to Entrez Gene ids

from collections import defaultdict

import pandas as pd

def parse_hgnc():
    """Determine HGNC to Entrez gene id mapping.

    Drops all genes without Entrez Gene ids.
    """

    file_url = "ftp://ftp.ebi.ac.uk/pub/databases/genenames/new/tsv/hgnc_complete_set.txt"

    # drops any HGNC genes with missing Entrez ids
    return (pd
        .read_csv(file_url, sep='\t', low_memory=False)
        [["hgnc_id", "symbol", "status", "entrez_id"]]
        .dropna(axis=0, how="any", subset=["entrez_id"])
        .assign(entrez_id = lambda df: df["entrez_id"].astype(int))
    )

def parse_umls(rrf_file):
    """Parse the UMLS to determine the HGNC identifier of each gene CUI.

    The relevant files are in the archive <version>-1-meta.nlm (a zip file)
    within <version>/META/MRCONSO.RRF.*.gz

    Concatenate the unzipped versions of the MRCONSO files together to get the
    final MRCONSO.RRF file, which is a | delimited text file without a header.
    """

    res = defaultdict(list)
    with open(rrf_file, "r") as fin:
        for line in fin:
            if "HGNC:" in line:
                vals = line.rstrip("\n").split("|")

                cui = vals[0]
                for val in vals[1:]:
                    if val.startswith("HGNC:"):
                        res["cui"].append(cui)
                        res["hgnc_id"].append(val)

    return pd.DataFrame(res).drop_duplicates()

def load_data(rrf_file):
    hgnc_map = parse_hgnc()
    cui_map = parse_umls(rrf_file)

    res = hgnc_map.merge(cui_map, how="inner", on="hgnc_id")

    for idx, row in res.iterrows():
        yield {
            "_id": str(row["entrez_id"]),
            "umls": {
                "cui": row["cui"]
            }
        }
