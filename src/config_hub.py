# ######### #
# HUB VARS  #
# ######### #

# Refer to biothings.hub.default_config for all configurable settings

DATA_SRC_SERVER = 'localhost'
DATA_SRC_PORT = 27017
DATA_SRC_DATABASE = 'mygene_src'

DATA_TARGET_SERVER = 'localhost'
DATA_TARGET_PORT = 27017
DATA_TARGET_DATABASE = 'mygene'

HUB_DB_BACKEND = {
    "module": "biothings.utils.mongo",
    "uri": "mongodb://localhost:27017",
}
DATA_HUB_DB_DATABASE = "mygene_hubdb"


# Hub name/icon url/version, for display purpose
HUB_NAME = "MyGene Hub (prod)"
HUB_ICON = "https://mygene.info/static/img/mygene-logo-shiny.svg"

# Pre-prod/test ES definitions
INDEX_CONFIG = {
    "indexer_select": {
        # default
        None: "hub.dataindex.indexer.GeneIndexer",
    },
    "env": {
        "prod": {
            "host": "<PRODSERVER>:9200",
            "indexer": {
                "args": {
                    "timeout": 300,
                    "retry_on_timeout": True,
                    "max_retries": 10,
                },
            },
            "index": [{"index": "genedoc_mygene_allspecies_current", "doc_type": "gene"}]
        },
        "local": {
            "host": "localhost:9200",
            "indexer": {
                "args": {
                    "timeout": 300,
                    "retry_on_timeout": True,
                    "max_retries": 10,
                },
            },
            "index": [{"index": "mygene_gene_allspecies_current", "doc_type": "gene"}]
        },
    },
}


# Snapshot environment configuration
SNAPSHOT_CONFIG = {
    "env": {
        "prod": {
            "cloud": {
                "type": "aws",  # default, only one supported by now
                "access_key": None,
                "secret_key": None,
            },
            "repository": {
                "name": "gene_repository-$(Y)",
                "type": "s3",
                "settings": {
                        "bucket": "<SNAPSHOT_BUCKET_NAME>",
                        "base_path": "mygene.info/$(Y)",  # per year
                        "region": "us-west-2",
                },
                "acl": "private",
            },
            "indexer": {
                # reference to INDEX_CONFIG
                "env": "local",
            },
            # when creating a snapshot, how long should we wait before querying ES
            # to check snapshot status/completion ? (in seconds)
            "monitor_delay": 60 * 5,
        },
        "demo": {
            "cloud": {
                "type": "aws",  # default, only one supported by now
                "access_key": None,
                "secret_key": None,
            },
            "repository": {
                "name": "gene_repository-demo-$(Y)",
                "type": "s3",
                "settings": {
                        "bucket": "<SNAPSHOT_DEMO_BUCKET_NAME>",
                        "base_path": "mygene.info/$(Y)",  # per year
                        "region": "us-west-2",
                },
                "acl": "public",
            },
            "indexer": {
                # reference to INDEX_CONFIG
                "env": "local",
            },
            # when creating a snapshot, how long should we wait before querying ES
            # to check snapshot status/completion ? (in seconds)
            "monitor_delay": 10,
        }
    }
}

# Release configuration
# Each root keys define a release environment (test, prod, ...)
RELEASE_CONFIG = {
    "env": {
        "prod": {
            "cloud": {
                "type": "aws",  # default, only one supported by now
                "access_key": None,
                "secret_key": None,
            },
            "release": {
                "bucket": "<RELEASES_BUCKET_NAME>",
                "region": "us-west-2",
                "folder": "mygene.info",
                "auto": True,  # automatically generate release-note ?
            },
            "diff": {
                "bucket": "<DIFFS_BUCKET_NAME>",
                "folder": "mygene.info",
                "region": "us-west-2",
                "auto": True,  # automatically generate diff ? Careful if lots of changes
            },
        },
        "demo": {
            "cloud": {
                "type": "aws",  # default, only one supported by now
                "access_key": None,
                "secret_key": None,
            },
            "release": {
                "bucket": "<RELEASES_BUCKET_NAME>",
                "region": "us-west-2",
                "folder": "mygene.info-demo",
                "auto": True,  # automatically generate release-note ?
            },
            "diff": {
                "bucket": "<DIFFS_BUCKET_NAME>",
                "folder": "mygene.info",
                "region": "us-west-2",
                "auto": True,  # automatically generate diff ? Careful if lots of changes
            },
        }
    }
}


# cached data (it None, caches won't be used at all)
CACHE_FOLDER = None

# when publishing releases, specify the targetted (ie. required) standalone version
STANDALONE_VERSION = {"branch": "standalone_v3"}

# Autohub configuration, either from a static definition...
STANDALONE_CONFIG = {
    "_default": {
        "es_host": "localhost:9200",
        "index": "mygene_test",
        "doc_type": "gene"
    },
    "mygene.info": {
        "es_host": "prodserver:9200",
        "index": "mygene_prod",
        "doc_type": "gene"
    },
}
# ... or using a dynamic indexer factory and ES host (index names are then
# taken from VERSION_URLS and all are managed on one given ES host)
#AUTOHUB_INDEXER_FACTORY = "biothings.hub.dataindex.indexer.DynamicIndexerFactory"
#AUTOHUB_ES_HOST = "localhost:9200"

# Autohub configuration, either from a static definition...
STANDALONE_CONFIG = {
    "_default": {
        "es_host": "localhost:9200",
        "index": "mygene_test",
        "doc_type": "gene"
    },
    "mygene.info": {
        "es_host": "prodserver:9200",
        "index": "mygene_prod",
        "doc_type": "gene"
    },
}
# ... or using a dynamic indexer factory and ES host (index names are then
# taken from VERSION_URLS and all are managed on one given ES host)
#AUTOHUB_INDEXER_FACTORY = "biothings.hub.dataindex.indexer.DynamicIndexerFactory"
#AUTOHUB_ES_HOST = "localhost:9200"


########################################
# APP-SPECIFIC CONFIGURATION VARIABLES #
########################################
# The following variables should or must be defined in your
# own application. Create a config.py file, import that config_common
# file as:
#
#   from config_hub import *
#
# then define the following variables to fit your needs. You can also override any
# any other variables in this file as required. Variables defined as ValueError() exceptions
# *must* be defined
#

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
