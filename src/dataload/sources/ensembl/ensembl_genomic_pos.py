from .ensembl_base import EnsemblParser
import biothings.dataload.uploader as uploader

class EnsemblGenomicPosUploader(uploader.MergerSourceUploader):

    name = "ensembl_genomic_pos"
    main_source = "ensembl"

    def load_data(self, data_folder):
        ep = EnsemblParser(data_folder)
        ensembl2pos = ep.load_ensembl2pos()
        return ensembl2pos

    def get_mapping(self):
        mapping = {
            "genomic_pos": {
                "dynamic": False,
                "type": "nested",                 # index as nested
                "properties": {
                    "chr": {"type": "string"},
                    "start": {"type": "long"},
                    "end": {"type": "long"},
                    "strand": {
                        "type": "byte",
                        "index": "no"
                    },
                },
            },
            "genomic_pos_hg19": {
                "dynamic": False,
                "type": "nested",                 # index as nested
                "properties": {
                    "chr": {"type": "string"},
                    "start": {"type": "long"},
                    "end": {"type": "long"},
                    "strand": {
                        "type": "byte",
                        "index": "no"
                    },
                },
            },
            "genomic_pos_mm9": {
                "dynamic": False,
                "type": "nested",                 # index as nested
                "properties": {
                    "chr": {"type": "string"},
                    "start": {"type": "long"},
                    "end": {"type": "long"},
                    "strand": {
                        "type": "byte",
                        "index": "no"
                    },
                },
            }
        }
        return mapping
