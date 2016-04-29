from .ucsc_base import load_ucsc_exons

__metadata__ = {
    '__collection__' : 'ucsc_exons',
    'structure': {
      'exons': None,
      'exons_hg19': None    # For human genes, default exons are on hg38,
                            # exons_hg19 were still kept there.
      },
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
