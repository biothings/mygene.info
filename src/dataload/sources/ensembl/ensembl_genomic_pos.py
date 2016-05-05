from .ensembl_base import EnsemblParser


__metadata__ = {
    '__collection__': 'ensembl_genomic_pos',
}


def load_genedoc(self=None):
    ep = EnsemblParser()
    ensembl2pos = ep.load_ensembl2pos()
    return ensembl2pos


def get_mapping(self=None):
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
