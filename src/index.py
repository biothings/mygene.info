"""
    Mygene Web Server Entry Point

    Examples:
>>> python index.py
>>> python index.py --debug
>>> python index.py --port=8000

"""
import os.path

import config
from biothings.web.launcher import main

ADDON_HANDLERS = [
    (r"/demo/?(.*)", "tornado.web.StaticFileHandler",
     {"path": "docs/demo", "default_filename": "index.html"}),
]
if config.INCLUDE_DOCS:
    if not os.path.exists(config.DOCS_STATIC_PATH):
        raise IOError('Run "make html" to generate sphinx docs first.')
    ADDON_HANDLERS += [
        (r"/widget/(.*)", "tornado.web.RedirectHandler", {"url": "/static/widget/{0}"}),
        (r"/?(.*)", "tornado.web.StaticFileHandler", {'path': config.DOCS_STATIC_PATH}),
    ]


if __name__ == '__main__':
    main(ADDON_HANDLERS)
