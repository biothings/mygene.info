import os.path
import time
from biothings.utils.common import timesofar
from biothings.utils.dataload import tab2dict, tabfile_feeder, list2dict

import logging
logging = logging.getLogger("exac_upload")

def load_broadinstitute_exac_any(one_file,key):
    logging.info("Loading file %s (%s)" % (one_file,key))
    data = tab2dict(one_file, (0,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21), 0)
    exacs = {}
    for transcript in data:
        tupleexac = data[transcript]
        # remove version in key so we can search the dict easily later
        exacs[transcript.split(".")[0]] = {"exac" : 
                {
                    "transcript" : transcript,  # but keep version here
                    "n_exons" : int(tupleexac[0]),
                    "cds_start" : int(tupleexac[1]),
                    "cds_end" : int(tupleexac[2]),
                    "bp" : int(tupleexac[3]),
                    key : {
                        "mu_syn" : float(tupleexac[4]),
                        "mu_mis" : float(tupleexac[5]),
                        "mu_lof" : float(tupleexac[6]),
                        "n_syn" : float(tupleexac[7]),
                        "n_mis" : float(tupleexac[8]),
                        "n_lof" : float(tupleexac[9]),
                        "exp_syn" : float(tupleexac[10]),
                        "exp_mis" : float(tupleexac[11]),
                        "exp_lof" : float(tupleexac[12]),
                        "syn_z" : float(tupleexac[13]),
                        "mis_z" : float(tupleexac[14]),
                        "lof_z" : float(tupleexac[15]),
                        "p_li" : float(tupleexac[16]),
                        "p_rec" : float(tupleexac[17]),
                        "p_null" : float(tupleexac[18])
                        }
                    }
                }
    return exacs


def load_broadinstitute_exac_nontcga(data_folder):
    nontcga_file = None
    for filename in os.listdir(data_folder):
        if filename.find("nonTCGA") >= 0:
            nontcga_file = filename
            break
    nontcga_file = os.path.join(data_folder, nontcga_file)
    return load_broadinstitute_exac_any(nontcga_file,"nontcga")


def load_broadinstitute_exac_nonpsych(data_folder):
    nonpsych_file = None
    for filename in os.listdir(data_folder):
        if filename.find("nonpsych") >= 0:
            nonpsych_file = filename
            break
    nonpsych_file = os.path.join(data_folder, nonpsych_file)
    return load_broadinstitute_exac_any(nonpsych_file,"nonpsych")


def load_broadinstitute_exac_all(data_folder):
    # find the file not containing tcga or nonpsych, that is, the one containing all
    # which unfortunately contains the release number...
    all_file = None
    for filename in os.listdir(data_folder):
        if filename.endswith(".log"):
            continue
        if filename.find("nonTCGA") == -1 and filename.find("nonpsych") == -1:
            all_file = filename
            break
    all_file = os.path.join(data_folder, all_file)
    return load_broadinstitute_exac_any(all_file,"all")


def load_broadinstitute_exac(data_folder):
    t0 = time.time()
    exacs = load_broadinstitute_exac_all(data_folder)
    for k,v in load_broadinstitute_exac_nontcga(data_folder).items():
        try:
            exacs[k]["exac"]["nontcga"] = v["exac"]["nontcga"]
        except KeyError:
            exacs[k] = v
    for k,v in load_broadinstitute_exac_nonpsych(data_folder).items():
        try:
            exacs[k]["exac"]["nonpsych"] = v["exac"]["nonpsych"]
        except KeyError:
            exacs[k] = v

    logging.info("Convert transcript ID to EntrezID")
    from ..ensembl.parser import EnsemblParser
    from biothings.utils.hub_db import get_src_dump
    ensembl_doc = get_src_dump().find_one({"_id":"ensembl"}) or {}
    ensembl_dir = ensembl_doc.get("data_folder")
    assert ensembl_dir, "Can't find Ensembl data directory (used for id conversion)"
    ensembl_parser = EnsemblParser(ensembl_dir)
    ensembl_parser._load_ensembl2entrez_li()
    ensembl2entrez = list2dict(ensembl_parser.ensembl2entrez_li, 0, alwayslist=True)
    for line in tabfile_feeder(os.path.join(ensembl_dir,"gene_ensembl__translation__main.txt")):
        _,ensid,transid,_ = line
        if transid in exacs:
            data = exacs.pop(transid) # pop so no-match means no data in the end
            for entrezid in ensembl2entrez.get(ensid,[ensid]):
                exacs[entrezid] = data

    return exacs
