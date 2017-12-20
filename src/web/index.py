# -*- coding: utf-8 -*-
# Simple template example used to instantiate a new biothing API
from biothings.web.index_base import main, options
from web.settings import MyGeneWebSettings
from tornado.web import StaticFileHandler
import os

# Instantiate settings class to configure biothings web
web_settings = MyGeneWebSettings(config='config')

if web_settings.INCLUDE_DOCS and not os.path.exists(web_settings.DOCS_STATIC_PATH):
    raise IOError('Run "make html" to generate sphinx docs first.')

APP_LIST = web_settings.generate_app_list()

if options.debug:
    APP_LIST += [
        (r"/widget/(.*)", StaticFileHandler, {'path': os.path.join(web_settings.STATIC_PATH, 'widget')}),
        (r"/?(.*)", StaticFileHandler, {'path': web_settings.DOCS_STATIC_PATH}),
    ]

if __name__ == '__main__':
    # set debug level on app settings
    web_settings.set_debug_level(options.debug)
    main(APP_LIST, debug_settings={"static_path": web_settings.STATIC_PATH},
         sentry_client_key=web_settings.SENTRY_CLIENT_KEY)
