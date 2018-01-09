# -*- coding: utf-8 -*-
from biothings.web.settings.default import *
from web.api.query_builder import ESQueryBuilder
from web.api.query import ESQuery
from web.api.transform import ESResultTransformer
from web.api.handlers import GeneHandler, QueryHandler, MetadataHandler, StatusHandler, TaxonHandler, DemoHandler, FrontPageHandler
import re

# *****************************************************************************
# Elasticsearch variables
# *****************************************************************************
# elasticsearch server transport url
ES_HOST = 'localhost:9200'
# elasticsearch index name
ES_INDEX = 'genedoc_mygene_allspecies_current'
# index for common species types
ES_INDEX_TIER1 = 'genedoc_mygene_current'
# elasticsearch document type
ES_DOC_TYPE = 'gene'

API_VERSION = 'v3'

# *****************************************************************************
# App URL Patterns
# *****************************************************************************
APP_LIST = [
    (r"/", FrontPageHandler),
    (r"/status", StatusHandler),
    (r"/metadata/?", MetadataHandler),
    (r"/metadata/fields/?", MetadataHandler),
    (r"/demo/?$", DemoHandler),
    (r"/{}/species/(\d+)/?".format(API_VERSION), TaxonHandler),
    (r"/{}/taxon/(\d+)/?".format(API_VERSION), TaxonHandler),
    (r"/{}/gene/(.+)/?".format(API_VERSION), GeneHandler),
    (r"/{}/gene/?$".format(API_VERSION), GeneHandler),
    (r"/{}/query/?".format(API_VERSION), QueryHandler),
    (r"/{}/metadata/?".format(API_VERSION), MetadataHandler),
    (r"/{}/metadata/fields/?".format(API_VERSION), MetadataHandler),
]

###############################################################################
#   app-specific query builder, query, and result transformer classes
###############################################################################

# *****************************************************************************
# Subclass of biothings.web.api.es.query_builder.ESQueryBuilder to build
# queries for this app
# *****************************************************************************
ES_QUERY_BUILDER = ESQueryBuilder
# *****************************************************************************
# Subclass of biothings.web.api.es.query.ESQuery to execute queries for this app
# *****************************************************************************
ES_QUERY = ESQuery
# *****************************************************************************
# Subclass of biothings.web.api.es.transform.ESResultTransformer to transform
# ES results for this app
# *****************************************************************************
ES_RESULT_TRANSFORMER = ESResultTransformer

GA_ACTION_QUERY_GET = 'query_get'
GA_ACTION_QUERY_POST = 'query_post'
GA_ACTION_ANNOTATION_GET = 'gene_get'
GA_ACTION_ANNOTATION_POST = 'gene_post'
GA_TRACKER_URL = 'MyGene.info'

# html header image
HTML_OUT_HEADER_IMG = "/static/favicon.ico"

# for title line on format=html
HTML_OUT_TITLE = """<p style="font-family:'Open Sans',sans-serif;font-weight:bold; font-size:16px;"><a href="http://mygene.info" target="_blank" style="text-decoration: none; color: black">MyGene.info - Gene Annotation as a Service</a></p>"""

METADATA_DOCS_URL = "http://docs.mygene.info/en/latest/doc/data.html"
QUERY_DOCS_URL = "http://docs.mygene.info/en/latest/doc/query_service.html"
ANNOTATION_DOCS_URL = "http://docs.mygene.info/en/latest/doc/annotation_service.html"

# kwargs for status check
STATUS_CHECK = {
    'id':'1017',
    'index': 'genedoc_mygene_allspecies_current',
    'doc_type': 'gene'
}

JSONLD_CONTEXT_PATH = 'web/context/context.json'

# MYGENE THINGS

# for error messages
ID_REQUIRED_MESSAGE = 'Gene ID Required'
ID_NOT_FOUND_TEMPLATE = "Gene ID '{bid}' not found"

# for docs
INCLUDE_DOCS = True
DOCS_STATIC_PATH = '../docs/_build/html'

# for static server
STATIC_PATH = 'static'

# url template to redirect for 'include_tax_tree' parameter
INCLUDE_TAX_TREE_REDIRECT_TEMPLATE = 'http://t.biothings.io/v1/taxon?ids={ids}&expand_species=true'

# This essentially bypasses the es.get fallback as in myvariant...
# The first regex matched integers, in which case the query becomes against entrezgeneall annotation queries are now multimatch
# against the following fields
ANNOTATION_ID_REGEX_LIST = [(re.compile(r'^\d+$'), ['entrezgene', 'retired']),
                            (re.compile(r'.*'), ['ensembl.gene'])]

DEFAULT_FIELDS = ['name', 'symbol', 'taxid', 'entrezgene']

TAXONOMY = {
    "human": {"tax_id": "9606", "assembly": "hg38"},
    "mouse": {"tax_id": "10090", "assembly": "mm10"},
    "rat": {"tax_id": "10116", "assembly": "rn4"},
    "fruitfly": {"tax_id": "7227", "assembly": "dm3"},
    "nematode": {"tax_id": "6239", "assembly": "ce10"},
    "zebrafish": {"tax_id": "7955", "assembly": "zv9"},
    "thale-cress": {"tax_id": "3702"},
    "frog": {"tax_id": "8364", "assembly": "xenTro3"}, 
    "pig": {"tax_id": "9823", "assembly": "susScr2"}
}

DATASOURCE_TRANSLATIONS = {
    "refseq:":  r"refseq.\\\*:",
    "accession:":   r"accession.\\\*:",
    "reporter:":    r"reporter.\\\*:",
    "interpro:":    r"interpro.\\\*:",
    # GO:xxxxx looks like a ES raw query, so just look for 
    # the term as a string in GO's ID (note: searching every keys
    # will raise an error because pubmed key is a int and we're 
    # searching with a string term.
    "GO:":          r"go.\\\*.id:go\\\:",
    #"GO:":          r"go.\\\*:go.",
    "homologene:":  r"homologene.\\\*:",
    "reagent:":     r"reagent.\\\*:",
    "uniprot:":     r"uniprot.\\\*:",
    "wikipedia:":   r"wikipedia.\\\*:",
    "ensemblgene:":         "ensembl.gene:",
    "ensembltranscript:":   "ensembl.transcript:",
    "ensemblprotein:":      "ensembl.protein:",

    # some specific datasources needs to be case-insentive
    "hgnc:":        r"HGNC:",
    "hprd:":        r"HPRD:",
    "mim:":        r"MIM:",
    "mgi:":        r"MGI:",
    "ratmap:":      r"RATMAP:",
    "rgd:":      r"RGD:",
    "flybase:":      r"FLYBASE:",
    "wormbase:":    r"WormBase:",
    "tair:":      r"TAIR:",
    "zfin:":      r"ZFIN:",
    "xenbase:":      r"Xenbase:",
    "mirbase:":     r"miRBase:",
}

SPECIES_TYPEDEF = {'species': {'type': list, 'default': ['all'], 'max': 1000, 
                   'translations': [(re.compile(pattern, re.I), translation['tax_id']) for (pattern, translation) in TAXONOMY.items()]}}

# For datasource translations
DATASOURCE_TRANSLATION_TYPEDEF = [(re.compile(pattern, re.I), translation) for 
    (pattern, translation) in DATASOURCE_TRANSLATIONS.items()]
TRIMMED_DATASOURCE_TRANSLATION_TYPEDEF = [(re.compile(re.sub(r':.*', '', pattern).replace('\\', ''), re.I), 
    re.sub(r':.*', '', translation).replace('\\','')) for (pattern, translation) in DATASOURCE_TRANSLATIONS.items()]

# Kwarg control update for mygene specific kwargs

# ES KWARGS (_source, scopes, 
#ANNOTATION_GET_ES_KWARGS['_source'].update({#'default': DEFAULT_FIELDS, 
#    'translations': TRIMMED_DATASOURCE_TRANSLATION_TYPEDEF})
#ANNOTATION_POST_ES_KWARGS['_source'].update({#'default': DEFAULT_FIELDS, 
#    'translations': TRIMMED_DATASOURCE_TRANSLATION_TYPEDEF})
QUERY_GET_ES_KWARGS['_source'].update({'default': DEFAULT_FIELDS})#, 'translations': TRIMMED_DATASOURCE_TRANSLATION_TYPEDEF})
QUERY_POST_ES_KWARGS['_source'].update({'default': DEFAULT_FIELDS})#, 'translations': TRIMMED_DATASOURCE_TRANSLATION_TYPEDEF})

# Control KWARGS
QUERY_GET_CONTROL_KWARGS['q'].update({'translations': DATASOURCE_TRANSLATION_TYPEDEF})

# query builder KWARGS
ANNOTATION_GET_ESQB_KWARGS.update(SPECIES_TYPEDEF)
ANNOTATION_POST_ESQB_KWARGS.update(SPECIES_TYPEDEF)
QUERY_GET_ESQB_KWARGS.update(SPECIES_TYPEDEF)
# ES query goes to these species by default?
#QUERY_GET_ESQB_KWARGS['species']['default'] = [9606, 10090, 10116]  
QUERY_GET_ESQB_KWARGS.update({
    'include_tax_tree': {'type': bool, 'default': False},
    'entrezonly':{'type': bool, 'default': False}, 
    'ensemblonly': {'type':bool, 'default': False}, 
    'exists': {'type': list, 'default': None, 'max': 1000}, 
    'missing': {'type': list, 'default': None, 'max': 1000}, 
    'species_facet_filter': {'type': list, 'default': None, 'max': 1000, 
        'translations': [(re.compile(pattern, re.I), translation['tax_id']) for 
                        (pattern, translation) in TAXONOMY.items()]}
})
QUERY_POST_ESQB_KWARGS.update(SPECIES_TYPEDEF)
QUERY_POST_ESQB_KWARGS['scopes'].update({'translations': TRIMMED_DATASOURCE_TRANSLATION_TYPEDEF})
