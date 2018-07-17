#############
Web component
#############

The BioThings SDK web component contains tools used to generate and customize an API, given an Elasticsearch index with data.  The web component uses the Tornado Web Server to respond to incoming API requests.

.. py:module:: biothings

******************
Server boot script
******************

.. automodule:: biothings.web.index_base

.. automethod:: biothings.web.index_base.main

********
Settings
********

.. automodule:: biothings.web.settings

Config module
=============

BiothingWebSettings
===================

.. autoclass:: biothings.web.settings.BiothingWebSettings
    :members:

BiothingESWebSettings
=====================

.. autoclass:: biothings.web.settings.BiothingESWebSettings
    :members:

********
Handlers
********

BaseHandler
===========

.. autoclass:: biothings.web.api.helper.BaseHandler
    :members:

BaseESRequestHandler
====================

.. autoclass:: biothings.web.api.es.handlers.base_handler.BaseESRequestHandler
    :members:

BiothingHandler
---------------

.. autoclass:: biothings.web.api.es.handlers.biothing_handler.BiothingHandler
    :members:

QueryHandler
------------

.. autoclass:: biothings.web.api.es.handlers.query_handler.QueryHandler
    :members:

MetadataHandler
---------------

.. autoclass:: biothings.web.api.es.handlers.metadata_handler.MetadataHandler
    :members:

***************************
Elasticsearch Query Builder
***************************

.. autoclass:: biothings.web.api.es.query_builder.ESQueries
    :members:

.. autoclass:: biothings.web.api.es.query_builder.ESQueryBuilder
    :members:

*******************
Elasticsearch Query
*******************

.. autoclass:: biothings.web.api.es.query.ESQuery
    :members:

********************************
Elasticsearch Result Transformer
********************************

.. autoclass:: biothings.web.api.es.transform.ESResultTransformer
    :members:
