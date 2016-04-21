from config_common import *

# ES_HOST = 'su07:9200'
ES_HOST = '52.32.23.166:9200'


# ES_INDEX_NAME = "genedoc_mygene_allspecies_current_3"
# ES_INDEX_NAME_TIER1 = "genedoc_mygene_current_3"
ES_INDEX_NAME = "genedoc_mygene_allspecies_current_2"
ES_INDEX_NAME_TIER1 = "genedoc_mygene_current_2"


ES_SCROLL_TIME = '10'
ES_SCROLL_SIZE = 10


# relevant for running in prod
INCLUDE_DOCS = False  # if True, include the links to mygene.info docs

# *****************************************************************************
# Google Analytics Settings
# *****************************************************************************
# Google Analytics Account ID
GA_ACCOUNT = 'UA-xxxxxxxx-x'
# Turn this to True to start google analytics tracking
GA_RUN_IN_PROD = False

