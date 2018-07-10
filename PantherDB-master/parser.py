import re
import os.path 

def load_data (data_folder):
         
         data_file = os.path.join(data_folder, "RefGenomeOrthologs") 
         
         # this empty dictionary is for storing the final output 
         d = {}
         # this empty list is for storing the orthologs of the same reference gene
         o = []
         # this empty list stores the common Uniprot_ID temporarily for comparison 
         e = None 
                  
         with open(data_file, "r+") as f:# change this to the file name
             # This function is for splitting the line
             for line in f:
                 y = re.split("[\| \t \n]", line)
                 z = re.split("=", y [2])
                 a = re.split("=", y [1])
                 b = re.split("=", y [4])
                 c = re.split("=", y [5])
                 ref_gene_uniprot_id = z [1]
                 ref_gene_db_name = a [0]
                 ref_gene_db_id = a[-1]
                 ortholog_db_name = b [0]
                 ortholog_db_id = b [-1]
                 ortholog_uniprot_id = c [1]
                 ortholog_type = y [6]
                 ortholog_family = y [8]
        
                 if e is None: # for the first item
                    e = ref_gene_uniprot_id
                    d = { "_id": ref_gene_uniprot_id,
                           "pantherdb": {
                           ref_gene_db_name: ref_gene_db_id,
                           "uniprot_kb": ref_gene_uniprot_id,
                           }
                        }
           
                 if ref_gene_uniprot_id != e: # if read up to a different ref. gene 
                      d ["pantherdb"] ["ortholog"] = o
                      yield d  
                      e = ref_gene_uniprot_id
                      d = { "_id": ref_gene_uniprot_id,
                            "pantherdb": {
                            ref_gene_db_name: ref_gene_db_id,
                            "uniprot_kb": ref_gene_uniprot_id
                            }
                          }
                      o = [{ortholog_db_name: ortholog_db_id,
                             "uniprot_kb": ortholog_uniprot_id,
                             "ortholog_type": ortholog_type,
                             "panther_family": ortholog_family
                             }
                          ]
        
                 else: # in this case the ref. gene is the same, just append the ortholog 
                     new = {ortholog_db_name: ortholog_db_id,
                            "uniprot_kb": ortholog_uniprot_id,
                            "ortholog_type": ortholog_type,
                            "panther_family": ortholog_family
                            }
                     o.append(new)

             if o: # for the final item, which does not go to the second "if" route for output 
                d ["pantherdb"] ["ortholog"] = o
                yield d       
                    
       
if "__name__" == "__main__":
    g = load_data(data_folder)
