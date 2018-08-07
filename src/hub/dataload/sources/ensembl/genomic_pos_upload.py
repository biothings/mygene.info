from .parser import EnsemblParser
import biothings.hub.dataload.uploader as uploader

class EnsemblGenomicPosUploader(uploader.MergerSourceUploader):

    name = "ensembl_genomic_pos"
    main_source = "ensembl"

    def load_data(self, data_folder):
        ep = EnsemblParser(data_folder)
        ensembl2pos = ep.load_ensembl2pos()
        return ensembl2pos

    @classmethod
    def get_mapping(klass):
        mapping = {
            "genomic_pos": {
                "dynamic": False,
                "type": "nested",                 # index as nested
                "properties": {
                    "chr": {
                        "normalizer" : "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "start": {"type": "long"},
                    "end": {"type": "long"},
                    "strand": {
                        "type": "byte",
                        "index": False
                    },
                },
            },
            "genomic_pos_hg19": {
                "dynamic": False,
                "type": "nested",                 # index as nested
                "properties": {
                    "chr": {
                        "normalizer" : "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "start": {"type": "long"},
                    "end": {"type": "long"},
                    "strand": {
                        "type": "byte",
                        "index": False
                    },
                },
            },
            "genomic_pos_mm9": {
                "dynamic": False,
                "type": "nested",                 # index as nested
                "properties": {
                    "chr": {
                        "normalizer" : "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "start": {"type": "long"},
                    "end": {"type": "long"},
                    "strand": {
                        "type": "byte",
                        "index": False
                    },
                },
            }
        }
        return mapping
