from config_hub import *


DATA_SRC_SERVER = "myhost" # Have tried to change this to my host name but it still failed to run
DATA_SRC_PORT = 27017
DATA_SRC_DATABASE = "tutorial_src" # not sure whether I need to change this to the Ensembl plant db we are using this time
DATA_SRC_SERVER_USERNAME = None
DATA_SRC_SERVER_PASSWORD = None

DATA_TARGET_SERVER = "myhost"
DATA_TARGET_PORT = 27017
DATA_TARGET_DATABASE = "tutorial"
DATA_TARGET_SERVER_USERNAME = None
DATA_TARGET_SERVER_PASSWORD = None

# I have kept this unchanged as it seems to be the default port according to MongoDB documentation 
HUB_DB_BACKEND = {
		"module" : "biothings.utils.sqlite3",
        "sqlite_db_folder" : "./db",
		}

# I have changed these to the paths that direct to files I would like to have my data in
# but the same error appears 
DATA_ARCHIVE_ROOT = "/tmp/tutorial" 
LOG_FOLDER = "/tmp/tutorial/logs" 
