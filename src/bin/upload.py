#!/usr/bin/env python

import sys
import os.path
from biothings.utils.common import get_class_from_classpath

def main(source):

    import biothings, config
    biothings.config_for_app(config)

    from biothings.dataload.uploader import SourceManager
    import dataload

    src_manager = SourceManager()
    src_manager.register_sources(dataload.__sources_dict__)
    src_manager.upload_src(source)

if __name__ == '__main__':
    # can pass "main_source" or "main_source.sub_source"
    main(sys.argv[1])
