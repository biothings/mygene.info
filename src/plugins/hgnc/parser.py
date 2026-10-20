"""
# HGNC Data Parser
# Former official symbols (prev_symbol) of human genes from the HGNC complete set.
"""

import csv
import os

from biothings.utils.dataload import normalized_value


def load_data(data_folder):
    """Yield {"_id": entrez gene id, "prev_symbol": ...} for genes HGNC has renamed.

    NCBI gene_info folds former symbols into Synonyms (our `alias` field), so this is
    the only source that tells a retired official symbol apart from a casual synonym.
    """
    infile = os.path.join(data_folder, "hgnc_complete_set.txt")
    with open(infile, newline="", encoding="utf-8") as f:
        # read columns by header name; their positions have shifted between releases
        for row in csv.DictReader(f, delimiter="\t"):
            entrez_id = row["entrez_id"].strip()
            if row["status"] != "Approved" or not entrez_id:
                continue
            seen = {row["symbol"].lower()}
            prev_symbols = []
            for symbol in row["prev_symbol"].split("|"):
                symbol = symbol.strip()
                if symbol and symbol.lower() not in seen:
                    seen.add(symbol.lower())
                    prev_symbols.append(symbol)
            if prev_symbols:
                yield {"_id": entrez_id, "prev_symbol": normalized_value(prev_symbols)}
