#############
# HUB VARS  #
#############
import os

DATA_HUB_DB_DATABASE = "taxonomy_hubdb"               # db containing the following (internal use)
DATA_SRC_MASTER_COLLECTION = 'src_master'             # for metadata of each src collections
DATA_SRC_DUMP_COLLECTION = 'src_dump'                 # for src data download information
DATA_SRC_BUILD_COLLECTION = 'src_build'               # for src data build information
DATA_SRC_BUILD_CONFIG_COLLECTION = 'src_build_config' # for src data build configuration

DATA_TARGET_MASTER_COLLECTION = 'db_master'

# reporting diff results, number of IDs to consider (to avoid too much mem usage)
MAX_REPORTED_IDS = 1000
# for diff updates, number of IDs randomly picked as examples when rendering the report
MAX_RANDOMLY_PICKED = 10

# where to store info about processes launched by the hub
RUN_DIR = '/tmp/run'

# Max queued jobs in job manager
# this shouldn't be 0 to make sure a job is pending and ready to be processed
# at any time (avoiding job submission preparation) but also not a huge number
# as any pending job will consume some memory).
MAX_QUEUED_JOBS = os.cpu_count() * 4

# Max number of *processes* hub can access to run jobs
HUB_MAX_WORKERS = int(os.cpu_count() / 4)

# Max memory usage before hub will prevent creating more jobs, in byte
# If None, no limit. It's a good practice to put a limit as the more processes
# are used, the more they consume memory even if nothing runs. With a limit, hub
# will recycle the process queue in order to limit the memory usage
HUB_MAX_MEM_USAGE = None

# when creating a snapshot, how long should we wait before querying ES
# to check snapshot status/completion ? (in seconds)
MONITOR_SNAPSHOT_DELAY = 10

# compressed cache files
CACHE_FORMAT = "xz"

# Hub environment (like, prod, dev, ...)
# Used to generate remote metadata file, like "latest.json", "versions.json"
# If non-empty, this constant will be used to generate those url, as a prefix
# with "-" between. So, if "dev", we'll have "dev-latest.json", etc...
# "" means production
HUB_ENV = ""

# ES snapshot name used for sending snapshot data
# (access controlled, uses key/secret)
SNAPSHOT_REPOSITORY = "taxon_repository"
# ES snapshot name accessible (usually using a URL)
# These two snapshot configs should point to
# the same location in a way. The different is the first 
# used access controller to write data, and the second is read-only
READONLY_SNAPSHOT_REPOSITORY ="taxonomy_url"

# bucket/folder containing releases
S3_DIFF_BUCKET = "biothings-diffs"
# bucket containing release informations
S3_RELEASE_BUCKET = "biothings-releases"
# what sub-folder should be used within diff bucket to upload diff files
S3_APP_FOLDER = "t.biothings.io"



# default logger for the hub
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging

# If you need notifications to hipchat, fill with "token",
# "roomid" and "from" keys to broadcast m#essage to a Hipchat room.
# 'host' is a hipchat's subdomain, and 'usertoken' is a valid user
# (real user) token, used to attach file to messages (hipchat requires
# a real user to do that...)
HIPCHAT_CONFIG = {
        #    'token': 'abdce',
        #    'roomid': 123456,
        #    'from': 'hub',
        #    'host' : 'xxxx.hipchat.com',
        #    'usertoken' : 'abcdefghijkl'
        }    

# SSH port for hub console
HUB_SSH_PORT = 8022

################################################################################
# HUB_PASSWD
################################################################################
# The format is a dictionary of 'username': 'cryptedpassword'
# Generate crypted passwords with 'openssl passwd -crypt'
HUB_PASSWD = {"guest":"9RKfd8gDuNf0Q"} 

# Temporarily required for biothings update hub (full/incr updates)
ES_INDEX_NAME = 'taxon_current'
ES_DOC_TYPE = 'taxon'
# used to directly index documents (usually the prod)
ES_HOST = 'localhost:9200'
# used to create snapshot internally before deploying to prod
ES_SNAPSHOT_HOST = 'localhost:9200'

# Role, when master, hub will publish data (updates, snapshot, etc...) that
# other instances can use (production, standalones)
BIOTHINGS_ROLE = "slave"

# key/secret to access AWS S3 (only used when publishing releases, role=master)
AWS_KEY = ''
AWS_SECRET = ''

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
# To be defined at application-level:

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
#        "sqlite_db_folder" : "./db",
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

# Path to a folder to store all downloaded files, logs, caches, etc...
DATA_ARCHIVE_ROOT = ConfigurationError("Define path to folder which will contain all downloaded data, cache files, etc...")
# this dir must be created manually
LOG_FOLDER = ConfigurationError("Define path to folder which will contain log files")
# Usually inside DATA_ARCHIVE_ROOT
#LOG_FOLDER = os.path.join(DATA_ARCHIVE_ROOT,'logs')

# Path to folder containing diff files
DIFF_PATH = ConfigurationError("Define path to folder which will contain output files from diff")
# Usually inside DATA_ARCHIVE_ROOT
#DIFF_PATH = os.path.join(DATA_ARCHIVE_ROOT,"diff")

# Path to folder containing release note files
RELEASE_PATH = ConfigurationError("Define path to folder which will contain release files")
# Usually inside DATA_ARCHIVE_ROOT                                                                                                                                                                                                     
#RELEASE_PATH = os.path.join(DATA_ARCHIVE_ROOT,"release")


