from .uniprot_base import load_pdb
import biothings.dataload.uploader as uploader


class UniprotPDBUploader(uploader.MergerSourceUploader):

    name = "uniprot_pdb"
    main_source = "uniprot"

    def load_data(self, data_folder):
        return load_pdb(data_folder)

    def get_mapping(self):
        mapping = {
            "pdb": {
                "type": "string",
                "index": "not_analyzed"     # PDB is case-sensitive here
            }
        }
        return mapping
