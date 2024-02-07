"""
    Mygene.info API v3
    https://mygene.info/v3/
"""

import re
import copy

from biothings.web.settings.default import APP_LIST, ANNOTATION_KWARGS, QUERY_KWARGS

# *****************************************************************************
# Elasticsearch Settings
# *****************************************************************************
ES_HOST = "localhost:9200"
ES_INDEX = "mygene_current"
ES_DOC_TYPE = "gene"

# *****************************************************************************
# Web Application
# *****************************************************************************
API_VERSION = "v3"
TAX_REDIRECT = "http://t.biothings.io/v1/taxon/{0}?include_children=1"
APP_LIST += [
    (r"/{ver}/species/(\d+)/?", "tornado.web.RedirectHandler", {"url": TAX_REDIRECT}),
    (r"/{ver}/taxon/(\d+)/?", "tornado.web.RedirectHandler", {"url": TAX_REDIRECT}),
    (r"/{ver}/query/?", "web.handlers.MygeneQueryHandler"),
    (r"/{ver}/metadata/?", "web.handlers.MygeneSourceHandler"),
    (r"/metadata/?", "web.handlers.MygeneSourceHandler"),
]

# html header image
HTML_OUT_HEADER_IMG = "/static/favicon.ico"

# for title line on format=html
HTML_OUT_TITLE = """<a href="http://mygene.info" target="_blank">MyGene.info - Gene Annotation as a Service</a>"""
METADATA_DOCS_URL = "http://docs.mygene.info/en/latest/doc/data.html"
QUERY_DOCS_URL = "http://docs.mygene.info/en/latest/doc/query_service.html"
ANNOTATION_DOCS_URL = "http://docs.mygene.info/en/latest/doc/annotation_service.html"

# *****************************************************************************
# User Input Control
# *****************************************************************************
DEFAULT_FIELDS = ["name", "symbol", "taxid", "entrezgene"]

TAXONOMY = {
    "human": {"tax_id": "9606", "assembly": "hg38"},
    "mouse": {"tax_id": "10090", "assembly": "mm39"},
    "rat": {"tax_id": "10116", "assembly": "rn6"},
    "fruitfly": {"tax_id": "7227", "assembly": "dm6"},
    "nematode": {"tax_id": "6239", "assembly": "ce11"},
    "zebrafish": {"tax_id": "7955", "assembly": "danRer11"},
    "thale-cress": {"tax_id": "3702", "assembly": "araTha1"},
    "frog": {"tax_id": "8364", "assembly": "xenTro9"},
    "pig": {"tax_id": "9823", "assembly": "susScr11"},
}

DATASOURCE_TRANSLATIONS = {
    "refseq:": r"refseq_agg:",
    "accession:": r"accession_agg:",
    "reporter:": r"reporter.\*:",
    "interpro:": r"interpro.id:",
    # GO:xxxxx looks like a ES raw query, so just look for
    # the term as a string in GO's ID (note: searching every keys
    # will raise an error because pubmed key is a int and we're
    # searching with a string term.
    "GO:": r"go.\*.id:go\:",
    # "GO:": r"go.\*:go.",
    "homologene:": r"homologene.id:",
    "reagent:": r"reagent.\*.id:",
    "uniprot:": r"uniprot.\*:",
    "wikipedia:": r"wikipedia.\*:",
    "ensemblgene:": "ensembl.gene:",
    "ensembltranscript:": "ensembl.transcript:",
    "ensemblprotein:": "ensembl.protein:",
    # some specific datasources needs to be case-insentive
    "hgnc:": r"HGNC:",
    "hprd:": r"HPRD:",
    "mim:": r"MIM:",
    "mgi:": r"MGI:",
    "ratmap:": r"RATMAP:",
    "rgd:": r"RGD:",
    "flybase:": r"FLYBASE:",
    "wormbase:": r"WormBase:",
    "tair:": r"TAIR:",
    "zfin:": r"ZFIN:",
    "sgd:": r"SGD:",
    "xenbase:": r"Xenbase:",
    "mirbase:": r"miRBase:",
}

SPECIES_TYPEDEF = {
    "species": {
        "type": list,
        "default": ["all"],
        "strict": False,
        "max": 1000,
        "translations": [
            (re.compile(pattern, re.I), translation["tax_id"])
            for (pattern, translation) in TAXONOMY.items()
        ],
    },
    "species_facet_filter": {
        "type": list,
        "default": None,
        "strict": False,
        "max": 1000,
        "translations": [
            (re.compile(pattern, re.I), translation["tax_id"])
            for (pattern, translation) in TAXONOMY.items()
        ],
    },
}
FIELD_FILTERS = {
    "entrezonly": {"type": bool, "default": False},
    "ensemblonly": {"type": bool, "default": False},
    "exists": {"type": list, "default": None, "max": 1000, "strict": False},
    "missing": {"type": list, "default": None, "max": 1000, "strict": False},
}

DATASOURCE_TRANSLATION_TYPEDEF = [
    (re.compile(pattern, re.I), translation)
    for (pattern, translation) in DATASOURCE_TRANSLATIONS.items()
]
TRIMMED_DATASOURCE_TRANSLATION_TYPEDEF = [
    (
        re.compile(re.sub(r":.*", "", pattern).replace("\\", "") + "(?!\\.)", re.I),
        re.sub(r":.*", "", translation).replace("\\", ""),
    )
    for (pattern, translation) in DATASOURCE_TRANSLATIONS.items()
]
ANNOTATION_KWARGS = copy.deepcopy(ANNOTATION_KWARGS)
ANNOTATION_KWARGS["*"].update(SPECIES_TYPEDEF)
ANNOTATION_KWARGS["*"]["_source"]["strict"] = False

QUERY_KWARGS = copy.deepcopy(QUERY_KWARGS)
QUERY_KWARGS["*"].update(SPECIES_TYPEDEF)
QUERY_KWARGS["*"].update(FIELD_FILTERS)
QUERY_KWARGS["*"]["_source"]["default"] = DEFAULT_FIELDS
QUERY_KWARGS["*"]["_source"]["strict"] = False
QUERY_KWARGS["GET"]["q"]["translations"] = DATASOURCE_TRANSLATION_TYPEDEF
QUERY_KWARGS["POST"]["scopes"]["translations"] = TRIMMED_DATASOURCE_TRANSLATION_TYPEDEF
QUERY_KWARGS["GET"]["include_tax_tree"] = {"type": bool, "default": False}
QUERY_KWARGS["POST"]["scopes"]["default"] = [
    "_id",
    "entrezgene",
    "ensembl.gene",
    "retired",
]
QUERY_KWARGS["POST"]["q"]["jsoninput"] = True


# *****************************************************************************
# Elasticsearch Query Pipeline
# *****************************************************************************
ES_QUERY_BUILDER = "web.pipeline.MygeneQueryBuilder"
AVAILABLE_FIELDS_EXCLUDED = ["all", "accession_agg", "refseq_agg"]

# *****************************************************************************
# Endpoints Specifics & Others
# *****************************************************************************

# kwargs for status check
STATUS_CHECK = {"id": "1017", "index": "mygene_current"}

# CURIE ID support based on BioLink Model
BIOLINK_MODEL_PREFIX_BIOTHINGS_GENE_MAPPING = {
    "NCBIGene": {"type": "gene", "field": ["entrezgene", "retired"]},
    "ENSEMBL": {"type": "gene", "field": "ensembl.gene"},
    "UniProtKB": {"type": "gene", "field": "uniprot.Swiss-Prot"},
}
biolink_curie_regex_list = []
for (
    biolink_prefix,
    mapping,
) in BIOLINK_MODEL_PREFIX_BIOTHINGS_GENE_MAPPING.items():
    expression = re.compile(rf"({biolink_prefix}):(?P<term>[^:]+)", re.I)
    field_match = mapping["field"]
    pattern = (expression, field_match)
    biolink_curie_regex_list.append(pattern)

# This essentially bypasses the es.get fallback as in myvariant ...
# The first regex matched integers, in which case the query becomes against
# entrezgeneall annotation queries are now multimatch against the following
# fields
fallback_pattern = (re.compile(r"^\d+$"), ["entrezgene", "retired"])

# The default pattern is neither the fallback pattern of the biolink
# CURIE ID prefixes match the pattern. This pattern matches the default
# presented in the ESQueryBuilder in the biothings.api library.
# Infers based off empty scopes
default_pattern = (re.compile(r"(?P<scope>[\W\w]+):(?P<term>[^:]+)"), [])

ANNOTATION_ID_REGEX_LIST = [
    *biolink_curie_regex_list,
    fallback_pattern,
    default_pattern,
]

ANNOTATION_DEFAULT_SCOPES = ["_id", "entrezgene", "ensembl.gene", "retired"]

# for docs
INCLUDE_DOCS = False
DOCS_STATIC_PATH = "docs/_build/html"

# url template to redirect for 'include_tax_tree' parameter
INCLUDE_TAX_TREE_REDIRECT_ENDPOINT = "http://t.biothings.io/v1/taxon"
