from .entrez_base import GeneSummaryParser

__metadata__ = {
    '__collection__': 'entrez_genesummary',
}


def load_data(self=None):
    gene2summary = GeneSummaryParser().load()
    return gene2summary


def get_mapping(self=None):
    mapping = {
        "summary": {
            "type": "string",
            "boost": 0.5      # downgrade summary field.
        },
    }
    return mapping
