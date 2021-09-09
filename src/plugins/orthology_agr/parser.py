
import os, pandas, csv, re
import numpy as np
from biothings.utils.dataload import dict_convert, dict_sweep

from biothings import config
logging = config.logger

process_key = lambda k: k.replace(" ","_").lower()

def load_orthology(data_folder):
    infile = os.path.join(data_folder, "ORTHOLOGY-ALLIANCE_COMBINED.tsv")
    assert os.path.exists(infile)
    data=pd.read_csv(f_in, header=15, sep="\\t").to_dict(orient='records')
    results = {}

    for rec in data:
        _id = rec['Gene1ID']
        rec = dict_convert(rec,keyfn=process_key)
        # remove NaN values, not indexable
        rec = dict_sweep(rec,vals=[np.nan])
        results.setdefault(_id,[]).append(rec)
        #print(rec)

    for _id,docs in results.items():
        doc = {"_id": _id, "orthology_data" : docs}
        yield doc
