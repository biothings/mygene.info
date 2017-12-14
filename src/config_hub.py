# ######### #
# HUB VARS  #
# ######### #
import os

DATA_HUB_DB_DATABASE = "gene_hubdb"         # db containing the following (internal use)
DATA_SRC_MASTER_COLLECTION = 'src_master'   # for metadata of each src collections
DATA_SRC_DUMP_COLLECTION = 'src_dump'       # for src data download information
DATA_SRC_BUILD_COLLECTION = 'src_build'     # for src data build information

DATA_TARGET_MASTER_COLLECTION = 'db_master'

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

# ES s3 repository to use snapshot/restore (must be pre-configured in ES)
SNAPSHOT_REPOSITORY = "gene_repository"
# ES snapshot name accessible (usually using a URL)
# These two snapshot configs should point to
# the same location in a way. The different is the first 
# used access controller to write data, and the second is read-only
READONLY_SNAPSHOT_REPOSITORY ="gene_url"

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

# when creating a snapshot, how long should we wait before querying ES
# to check snapshot status/completion ? (in seconds)
# Since myvariant's indices are pretty big, a whole snaphost won't happen in few secs,
# let's just monitor the status every 5min
MONITOR_SNAPSHOT_DELAY = 5 * 60

# Hub environment (like, prod, dev, ...)
# Used to generate remote metadata file, like "latest.json", "versions.json"
# If non-empty, this constant will be used to generate those url, as a prefix 
# with "-" between. So, if "dev", we'll have "dev-latest.json", etc...
# "" means production
HUB_ENV = ""

# S3 bucket, root of all biothings releases information
S3_RELEASE_BUCKET = "biothings-releases"
# S3 bucket, root of all biothings diffs
S3_DIFF_BUCKET = "biothings-diffs"
# what sub-folder should be used within diff bucket to upload diff files
S3_APP_FOLDER = "mygene.info" # gene/gene_allspecies

ES_DOC_TYPE = "gene" # also used during snapshot
# Pre-prod/test ES definitions
# (see bt.databuild.backend.create_backend() for the notation)
ES_TEST_HOST = 'localhost:9200'
ES_TEST_GENE = (ES_TEST_HOST,"mygene_gene_current","gene")
ES_TEST_GENE_ALLSPECIES = (ES_TEST_HOST,"mygene_gene_allspecies_current","gene")
# Prod ES definitions
ES_PROD_HOST = 'prodserver:9200'
ES_PROD_GENE = (ES_PROD_HOST,"mygene_gene_current","gene")
ES_PROD_GENE_ALLSPECIES = (ES_PROD_HOST,"mygene_gene_allspecies_current","gene")


# fill with "token", "roomid" and "from" keys
# to broadcast message to a Hipchat room
HIPCHAT_CONFIG = {
#    'token': '',
#    "usertoken" : "",
#    'roomid': '',
#    'from': '',
#    'host': '',
}

# SSH port for hub console
HUB_SSH_PORT = 8022

################################################################################
# HUB_PASSWD
################################################################################
# The format is a dictionary of 'username': 'cryptedpassword'
# Generate crypted passwords with 'openssl passwd -crypt'
HUB_PASSWD = {"guest":"9RKfd8gDuNf0Q"}

# cached data (it None, caches won't be used at all)
CACHE_FOLDER = None

# Role, when master, hub will publish data (updates, snapshot, etc...) that
# other instances can use (production, standalones)
BIOTHINGS_ROLE = "slave"

import logging
from biothings.utils.loggers import setup_default_log

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
from biothings import ConfigurationError

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

ES_HOST = ConfigurationError("Define ElasticSearch host used for index creation (eg localhost:9200)")

# Path to a folder to store all downloaded files, logs, caches, etc...
DATA_ARCHIVE_ROOT = ConfigurationError("Define path to folder which will contain all downloaded data, cache files, etc...")

# Path to folder containing diff files
DIFF_PATH = ConfigurationError("Define path to folder which will contain output files from diff")
# Usually inside DATA_ARCHIVE_ROOT
#DIFF_PATH = os.path.join(DATA_ARCHIVE_ROOT,"diff")

# Path to folder containing release note files
RELEASE_PATH = ConfigurationError("Define path to folder which will contain release files")
# Usually inside DATA_ARCHIVE_ROOT
#RELEASE_PATH = os.path.join(DATA_ARCHIVE_ROOT,"release")

# this dir must be created manually
LOG_FOLDER = ConfigurationError("Define path to folder which will contain log files")
# Usually inside DATA_ARCHIVE_ROOT
#LOG_FOLDER = os.path.join(DATA_ARCHIVE_ROOT,'logs')

# default hub logger
logger = ConfigurationError("Provide a default hub logger instance (use setup_default_log(name,log_folder)")
# Usually use default setup
#logger = setup_default_log("hub", LOG_FOLDER)

