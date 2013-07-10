.. MyGene.info documentation master file, created by
   sphinx-quickstart on Wed May 29 17:15:29 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. cssclass:: hidden-title
Home
****


MyGene.info : Gene Annotation Query as a Service
*************************************************

.. image:: _static/logo.png
   :align: left

.. cssclass:: head-paragraph

  `MyGene.info <http://mygene.info>`_ provides simple-to-use REST web services to query/retrieve gene annotation data. It's designed with **simplicity** and **performance** emphasized. A typical use case is to use it to power a web application which requires querying genes and obtaining common gene annotations. For example, `MyGene.info <http://mygene.info>`_ services are used to power `BioGPS <http://biogps.org>`_.

.. raw:: html

    <p id="status">
    <span id="status_text"></span>
    </p>
    <script type="text/javascript" src="_static/get_meta.js" charset="utf-8"></script>

.. container:: mg-citation

    To cite MyGene.info::

        Wu C, MacLeod I, Su AI (2013) BioGPS and MyGene.info: organizing online, gene-centric information. Nucl. Acids Res. 41(D1): D561-D565.


What's new in v2 API
------------------------

* **ALL** species are supported now! That's about 12,000 in total. [`more <doc/data.html#species>`_]
* Gene annotation data are even more `up-to-date <doc/data.html#data-sources>`_ (weekly updates).
* Gene query service supports `"fields" parameter <doc/query_service.html#fields>`_ to return any fields. Previously, you need to call gene query service separately if you need more than gene symbols and names.
* Fine-tuned query algorithm to return relevant gene hits first.
* Our query backend is more scalable and extensible. Ready to expand more annotation data as we go.

`Migration guide from v1 to v2 API <doc/migration_from_v1.html>`_

Still want to stick with v1 API for a while? It's still there: `v1 API </v1/doc>`_, but annotation data there won't updated any more.

.. include :: doc/quick_start.rst


Documentation
---------------------

.. toctree::
   :maxdepth: 3

   Try it live on interactive API page <http://mygene.info/v2/api>
   doc/migration_from_v1
   doc/data
   doc/query_service
   doc/annotation_service
   doc/usage_demo
   doc/packages
   terms


FAQ
-------

How many species are supported?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We support **ALL** species available from NCBI and Ensembl. `See more <doc/data.html#species>`_.

How frequent are the gene annotation data updated?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Gene annotation data are regularly updated once a week to keep it up-to-date. The most updated data information can be accessed `here </v2/metadata>`_. `See more <doc/data.html#data-sources>`_.


What's behind MyGene.info?
^^^^^^^^^^^^^^^^^^^^^^^^^^

`MyGene.info <http://mygene.info>`_ is built on `ElasticSearch <http://www.elasticsearch.org>`_, a document-based database and powerful query engine. Unlike more commonly used relational database systems (e.g., Oracle, MySQL), data are stored as "key-document" pairs. The "document" is a JSON-formatted gene annotation object, while the "key" is a gene ID (Entrez or Ensembl). The hierarchical structure of gene annotation data can be represented naturally in this key-document model. This simple object structure in ElasticSearch greatly simplified both data loading and data queries, and also gains impressive query performance and flexibility.

On top of ElasticSearch, we use `tornado <http://www.tornadoweb.org>`_, a lightweighted and fast web framework in python, to build our application layer. And then `Nginx <http://nginx.org>`_ is used as the front-end to serve outside requests.


Is this project open-sourced?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yes, this project is open-sourced under Apache license. The source code of `MyGene.info <http://mygene.info>`_ are hosted at `bitbucket <https://bitbucket.org/newgene/genedoc/src>`_


Who is using MyGene.info?
^^^^^^^^^^^^^^^^^^^^^^^^^

* `BioGPS <http://biogps.org>`_


Contact us
-------------------------

Your feedback to <help@mygene.info> is welcome.


.. raw:: html

    <div id="spacer" style="height:300px"></div>


.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
