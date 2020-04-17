"""
    Mygene Web Server Entry Point

    Examples:
>>> python index.py
>>> python index.py --debug
>>> python index.py --port=8000

"""
import os.path

from tornado.web import StaticFileHandler

import config
from biothings.web.index_base import main

if config.INCLUDE_DOCS:
    if not os.path.exists(config.DOCS_STATIC_PATH):
        raise IOError('Run "make html" to generate sphinx docs first.')
    else:
        config.APP_LIST += [
            (r"/widget/(.*)", StaticFileHandler, {
                'path': os.path.join(config.STATIC_PATH, 'widget')}),
            (r"/?(.*)", StaticFileHandler, {
                'path': config.DOCS_STATIC_PATH}),
        ]


if __name__ == '__main__':
    main()
