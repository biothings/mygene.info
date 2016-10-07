#!/usr/bin/env python

import sys

import biothings, config
biothings.config_for_app(config)

from biothings.dataload.dispatch import DocDispatcher

if __name__ == "__main__":
    dispatcher = DocDispatcher()
    dispatcher.run(sys.argv)
