import os

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import DummyDumper


class EntrezUnigeneDumper(DummyDumper):
    """No-op dumper for collection-only sources (data already in mongo,
    nothing downloadable anymore). Exists so DumperManager can register
    the source instead of logging tracebacks at every hub start.

    DISABLED so dump_all()/schedule_all() skip it entirely -- there is
    nothing to download, and running DummyDumper.dump() would overwrite
    download.release with an empty string."""

    SRC_NAME = "entrez_unigene"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    DISABLED = True
    AUTO_UPLOAD = False
