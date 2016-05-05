from .ucsc_base import load_ucsc_exons

__metadata__ = {
    '__collection__': 'ucsc_exons',
}


def load_genedoc(self=None):
    genedoc_d = load_ucsc_exons()
    return genedoc_d


def get_mapping(self=None):
    mapping = {
        #do not index exons
        "exons":  {
            "type": "object",
            "enabled": False
        },
        #do not index exons_hg19
        "exons_hg19":  {
            "type": "object",
            "enabled": False
        },
        "exons_mm9":  {
            "type": "object",
            "enabled": False
        }
    }
    return mapping
