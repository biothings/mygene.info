import sys

import biothings, config
biothings.config_for_app(config)
from biothings.dataload.dispatch import DocDispatcher

dispatcher = DocDispatcher()
dispatcher.run(sys.argv)
