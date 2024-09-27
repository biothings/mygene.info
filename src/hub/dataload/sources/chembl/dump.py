import biothings

import config

biothings.config_for_app(config)
import biothings.hub.dataload.dumper as dumper


class ChemblDumper(dumper.DummyDumper):
    SRC_NAME = "chembl"
