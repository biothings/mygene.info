# -*- coding: utf-8 -*-
# Simple template example used to instantiate a new biothing API
from biothings.www.index_base import main, options
from www.settings import MyGeneWebSettings

# Instantiate settings class to configure biothings web
web_settings = MyGeneWebSettings(config='config')

if __name__ == '__main__':
    # set debug level on app settings
    web_settings.set_debug_level(options.debug)
    main(web_settings.generate_app_list(), debug_settings={"STATIC_PATH": web_settings.STATIC_PATH},
         sentry_client_key=web_settings.SENTRY_CLIENT_KEY)
