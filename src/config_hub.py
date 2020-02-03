# ######### #
# HUB VARS  #
# ######### #
import os

DATA_HUB_DB_DATABASE = "gene_hubdb"         # db containing the following (internal use)
DATA_SRC_MASTER_COLLECTION = 'src_master'   # for metadata of each src collections
DATA_SRC_DUMP_COLLECTION = 'src_dump'       # for src data download information
DATA_SRC_BUILD_COLLECTION = 'src_build'     # for src data build information
DATA_PLUGIN_COLLECTION = 'data_plugin'     # for data plugins information
API_COLLECTION = 'api'                     # for api information (running under hub control)
CMD_COLLECTION = 'cmd'                     # for launched/running commands in shell
EVENT_COLLECTION = 'event'                 # for launched/running commands in shell

# where to store info about processes launched by the hub
RUN_DIR = './run'

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

# reporting diff results, number of IDs to consider (to avoid too much mem usage)
MAX_REPORTED_IDS = 1000
# for diff updates, number of IDs randomly picked as examples when rendering the report
MAX_RANDOMLY_PICKED = 10
# size of a diff file when in memory (used when merged/reduced)
MAX_DIFF_SIZE = 50 * 1024**2  # 50MiB (~1MiB on disk when compressed)

# cache file format ("": ascii/text uncompressed, or "gz|zip|xz"
CACHE_FORMAT = "xz"

# How much memory hub is allowed to use:
# - "auto", let hub decides (will use 50%-60% of available RAM)
# - None: no limit
# - otherwise specify a number in bytes
HUB_MAX_MEM_USAGE = None

# Max number of *processes* hub can access to run jobs
HUB_MAX_WORKERS = int(os.cpu_count() / 4)
MAX_SYNC_WORKERS = HUB_MAX_WORKERS

# Max queued jobs in job manager
# this shouldn't be 0 to make sure a job is pending and ready to be processed
# at any time (avoiding job submission preparation) but also not a huge number
# as any pending job will consume some memory).
MAX_QUEUED_JOBS = os.cpu_count() * 4

# Hub environment (like, prod, dev, ...)
# Used to generate remote metadata file, like "latest.json", "versions.json"
# If non-empty, this constant will be used to generate those url, as a prefix 
# with "-" between. So, if "dev", we'll have "dev-latest.json", etc...
# "" means production
HUB_ENV = ""

# Hub name/icon url/version, for display purpose
HUB_NAME = "MyGene"
HUB_ICON = "http://mygene.info/static/img/mygene-logo-shiny.svg"

### Pre-prod/test ES definitions
INDEX_CONFIG = {
		"indexer_select": {
			# default
			None : "hub.dataindex.indexer.GeneIndexer",
			},
		"env" : {
			"prod" : {
				"host" : "<PRODSERVER>:9200",
				"indexer" : {
					"args" : {
						"timeout" : 300,
						"retry_on_timeout" : True,
						"max_retries" : 10,
						},
					},
				"index" : [{"index": "genedoc_mygene_allspecies_current", "doc_type": "gene"}]
				},
			"test" : {
				"host" : "localhost:9200",
				"indexer" : {
					"args" : {
						"timeout" : 300,
						"retry_on_timeout" : True,
						"max_retries" : 10,
						},
					},
				"index" : [{"index": "mygene_gene_allspecies_current", "doc_type": "gene"}]
				},
			},
		}


# Snapshot environment configuration
SNAPSHOT_CONFIG = {
        "env" : {
            "prod" : {
                "cloud" : {
                    "type" : "aws", # default, only one supported by now
                    "access_key" : None,
                    "secret_key" : None,
                    },
                "repository" : {
                    "name" : "gene_repository",
                    "type" : "s3",
                    "settings" : {
                        "bucket" : "biothings-es6-snapshots-test",
                        "base_path" : "mygene.info/$(Y)", # per year
                        "region" : "us-west-2",
                        },
                    "acl" : "private",
                    },
                "indexer" : {
                    # reference to INDEX_CONFIG
                    "env" : "prod",
                    },
                # when creating a snapshot, how long should we wait before querying ES
                # to check snapshot status/completion ? (in seconds)
                "monitor_delay" : 60 * 5,
                },
            "demo" : {
                "cloud" : {
                    "type" : "aws", # default, only one supported by now
                    "access_key" : None,
                    "secret_key" : None,
                    },
                "repository" : {
                    "name" : "gene_repository-demo",
                    "type" : "s3",
                    "settings" : {
                        "bucket" : "biothings-es6-snapshots-demo-test",
                        "base_path" : "mygene.info/$(Y)", # per year
                        "region" : "us-west-2",
                        },
                    "acl" : "public",
                    },
                "indexer" : {
                    # reference to INDEX_CONFIG
                    "env" : "test",
                    },
                # when creating a snapshot, how long should we wait before querying ES
                # to check snapshot status/completion ? (in seconds)
                "monitor_delay" : 10,
                }
            }
        }

# Release configuration
# Each root keys define a release environment (test, prod, ...)
RELEASE_CONFIG = {
        "env" : {
            "prod" : {
                "cloud" : {
                    "type" : "aws", # default, only one supported by now
                    "access_key" : None,
                    "secret_key" : None,
                    },
                "release" : {
                    "bucket" : "biothings-releases-test",
                    "region" : "us-west-2",
                    "folder" : "mygene.info",
                    "auto" : True, # automatically generate release-note ?
                    },
                "diff" : {
                    "bucket" : "biothings-diffs-test",
                    "folder" : "mygene.info",
                    "region" : "us-west-2",
                    "auto" : True, # automatically generate diff ? Careful if lots of changes
                    },
                },
            "demo": {
                "cloud" : {
                    "type" : "aws", # default, only one supported by now
                    "access_key" : None,
                    "secret_key" : None,
                    },
                "release" : {
                    "bucket" : "biothings-releases-test",
                    "region" : "us-west-2",
                    "folder" : "mygene.info-demo",
                    "auto" : True, # automatically generate release-note ?
                    },
                "diff" : {
                    "bucket" : "biothings-diffs-demo-test",
                    "folder" : "mygene.info",
                    "region" : "us-west-2",
                    "auto" : True, # automatically generate diff ? Careful if lots of changes
                    },
                }
            }
        }

SLACK_WEBHOOK = None

# SSH port for hub console
HUB_SSH_PORT = 7022
HUB_API_PORT = 7080

################################################################################
# HUB_PASSWD
################################################################################
# The format is a dictionary of 'username': 'cryptedpassword'
# Generate crypted passwords with 'openssl passwd -crypt'
HUB_PASSWD = {"guest":"9RKfd8gDuNf0Q"}

# cached data (it None, caches won't be used at all)
CACHE_FOLDER = None

# when publishing releases, specify the targetted (ie. required) standalone version
STANDALONE_VERSION = "standalone_v3"

import logging

# don't bother with elements order in a list when diffing,
# mygene optmized uploaders can't produce different results
# when parsing data (parallelization)
import importlib
import biothings.utils.jsondiff
importlib.reload(biothings.utils.jsondiff)
biothings.utils.jsondiff.UNORDERED_LIST = True

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
from biothings import ConfigurationError, ConfigurationDefault, ConfigurationValue

# Individual source database connection
DATA_SRC_SERVER = ConfigurationError("Define hostname for source database")
DATA_SRC_PORT = ConfigurationError("Define port for source database")
DATA_SRC_DATABASE = ConfigurationError("Define name for source database")
DATA_SRC_SERVER_USERNAME = ConfigurationError("Define username for source database connection (or None if not needed)")
DATA_SRC_SERVER_PASSWORD = ConfigurationError("Define password for source database connection (or None if not needed)")

# Target (merged collection) database connection
DATA_TARGET_SERVER = ConfigurationError("Define hostname for target database (merged collections)")
DATA_TARGET_PORT = ConfigurationError("Define port for target database (merged collections)")
DATA_TARGET_DATABASE = ConfigurationError("Define name for target database (merged collections)")
DATA_TARGET_SERVER_USERNAME = ConfigurationError("Define username for target database connection (or None if not needed)")
DATA_TARGET_SERVER_PASSWORD = ConfigurationError("Define password for target database connection (or None if not needed)")

HUB_DB_BACKEND = ConfigurationError("Define Hub DB connection")
# Internal backend. Default to mongodb
# For now, other options are: mongodb, sqlite3, elasticsearch
#HUB_DB_BACKEND = {
#        "module" : "biothings.utils.sqlite3",
#        "sqlite_db_foder" : "./db",
#        }
#HUB_DB_BACKEND = {
#        "module" : "biothings.utils.mongo",
#        "uri" : "mongodb://localhost:27017",
#        #"uri" : "mongodb://user:passwd@localhost:27017", # mongodb std URI
#        }
#HUB_DB_BACKEND = {
#        "module" : "biothings.utils.es",
#        "host" : "localhost:9200",
#        }

# List of package paths for active datasources (expect data-plugin based sources)
ACTIVE_DATASOURCES = ConfigurationDefault(
        default=[],
        desc="List of package paths for active datasources")

# Path to a folder to store all downloaded files, logs, caches, etc...
DATA_ARCHIVE_ROOT = ConfigurationError("Define path to folder which will contain all downloaded data, cache files, etc...")

# Path to a folder to store all 3rd party parsers, dumpers, etc...
DATA_PLUGIN_FOLDER = ConfigurationDefault(
        default="./plugins",
        desc="Define path to folder which will contain all 3rd party parsers, dumpers, etc...")

# Path to folder containing diff files
DIFF_PATH = ConfigurationDefault(
        default=ConfigurationValue("""os.path.join(DATA_ARCHIVE_ROOT,"diff")"""),
        desc="Define path to folder which will contain output files from diff")
# Usually inside DATA_ARCHIVE_ROOT
#DIFF_PATH = os.path.join(DATA_ARCHIVE_ROOT,"diff")

# Path to folder containing release note files
RELEASE_PATH = ConfigurationDefault(
        default=ConfigurationValue("""os.path.join(DATA_ARCHIVE_ROOT,"release")"""),
        desc="Define path to folder which will contain release files")

# Usually inside DATA_ARCHIVE_ROOT
#RELEASE_PATH = os.path.join(DATA_ARCHIVE_ROOT,"release")

# this dir must be created manually
LOG_FOLDER = ConfigurationDefault(
        default=ConfigurationValue("""os.path.join(DATA_ARCHIVE_ROOT,"logs")"""),
        desc="Define path to folder which will contain log files")
# Usually inside DATA_ARCHIVE_ROOT
#LOG_FOLDER = os.path.join(DATA_ARCHIVE_ROOT,'logs')

# default hub logger
from biothings.utils.loggers import setup_default_log
logger = ConfigurationDefault(
        default=logging,
        desc="Provide a default hub logger instance (use setup_default_log(name,log_folder)")
# Usually use default setup
#logger = setup_default_log("hub", LOG_FOLDER)

