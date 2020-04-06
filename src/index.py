"""
    Mygene Web Server Entry Point

    Examples:
>>> python index.py
>>> python index.py --debug
>>> python index.py --port=8000

"""
import os.path

from biothings.web import BiothingsAPI
from tornado.options import define, options
from tornado.web import StaticFileHandler

import config

if config.INCLUDE_DOCS and not os.path.exists(config.DOCS_STATIC_PATH):
    raise IOError('Run "make html" to generate sphinx docs first.')


define("port", default=8000, type=int, help="run on the given port")
define("debug", default=False, type=bool, help="enable debug mode settings")


def main():

    options.parse_command_line()
    if options.debug:
        config.APP_LIST += [
            (r"/widget/(.*)", StaticFileHandler, {
                'path': os.path.join(config.STATIC_PATH, 'widget')}),
            (r"/?(.*)", StaticFileHandler, {
                'path': config.DOCS_STATIC_PATH}),
        ]

    api = BiothingsAPI(config)
    api.debug(options.debug)
    api.start(options.port)


if __name__ == '__main__':
    main()
