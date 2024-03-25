"""
# Orthology AGR Data Parser  
# Organization: Su and Wu labs @ Scripps Research  
# Data parser for the Alliance of Genome Resources database for ortholog relationships. 
"""
# load packages
import os
from biothings_client import get_client
import biothings.utils.dataload as dl

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

def get_entrez_id(gene_id, gene_client, bad_queries):
    """
        Use the biothings_client package to query the mygene.info db for 
        the corresponding entrezgene(NCBI gene) ID for the given gene_id
        gene_id: given id to search on
        gene_client: initialized object for connection to mygene.info 
    """
    #gene_client = get_client('gene') # initialize mygene object
    if "WB:" in gene_id: gene_id=gene_id.replace("WB:", "WormBase:")
    if "FB:" in gene_id: gene_id=gene_id.replace("FB:", "FLYBASE:")
    if "MGI:" in gene_id: gene_id=gene_id.replace("MGI:", "mgi:MGI\:")
    #gene=gene_client.getgene(gene_id, fields='symbol,name')

    #print("[INFO] searching for gene id ", gene_id)
    gene=gene_client.query(gene_id, fields='symbol,name') # get search results
    # check if gene id was not found
    if not gene["hits"]:
        #print("[INFO] Failed query on ID %s "%gene_id)
        bad_queries.append(gene_id)
    else:
        #print("[INFO] Success query on ID %s "%gene_id)
        gene_id=gene["hits"][0]["_id"]

    return gene_id;


def load_orthology(data_folder):
    """
        Main Method - data plugin parser for ortholog data from AGR
        data_folder: input folder (standard for biothings studio plugin)
    """

    # setup data from the file
    print("[INFO] loading orthology AGR data....")
    infile = os.path.join(data_folder, "ORTHOLOGY-ALLIANCE_COMBINED.tsv")
    assert os.path.exists(infile)

    gene_client = get_client('gene')
    records=[]# initialize record list for orthologs
    gene_dict={}

    bad_queries=[] # initialize gene query ids that return None (empty)

    # use dataload from biothings util to load tsv file
    for i, x in enumerate(list(dl.tabfile_feeder(infile, header=15, sep="\t"))):
        # pull out first row for the column header names
        if i == 0: cols_names=x, print('[COLS] %s \n'%" ".join(x))
        # if it isn't the first row, continue with id record
        else:
            # initialize data holders
            gene_id=get_entrez_id(x[0], gene_client, bad_queries)
            ortholog_id=get_entrez_id(x[4], gene_client, bad_queries)

        
            if gene_id not in gene_dict.keys(): 

                gene_dict[gene_id]={"orthologs": []}

            # setup dictionary record
            ortholog_dict={
                "geneid": ortholog_id,
                "symbol": x[5],
                "taxid": int(float(x[6].split(":")[1])),
                "algorithmsmatch": x[9],
                "outofalgorithms": x[10],
                "isbestscore": convert_score(x[11]),
                "isbestrevscore": convert_score(x[12])
            }
            gene_dict[gene_id]["orthologs"].append(ortholog_dict)

    gene_list=sorted(gene_dict.items())

    for d in gene_list:
        _id = d[0]  
        ortholog_dict=d[1]
    
        record= {
                "_id": _id,
                "agr":ortholog_dict
                }
        records.append(record)

    return records;