.. MyGene.info documentation master file, created by
   sphinx-quickstart on Wed May 29 17:15:29 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.



MyGene.info documentation
*************************

Introduction
-------------

.. image:: _static/logo.png
   :align: left

.. cssclass:: head-paragraph

  `MyGene.info <http://mygene.info>`_ provides simple-to-use REST web services to query/retrieve gene annotation data. It's designed with **simplicity** and **performance** emphasized. A typical use case is to use it to power a web application which requires querying genes and obtaining common gene annotations. For example, `MyGene.info <http://mygene.info>`_ services are used to power `BioGPS <http://biogps.org>`_.

.. raw:: html

    <style>
    #status {
        margin:0!important;
        line-height:1em!important;
    }

    #status span{
        margin-left:auto;
        margin-right:auto;
        width: 100%;
        display: block;
        text-align: center;
        font-weight: bold;
        font-family: "Open Sans", Arial, sans-serif !important;
    }
    </style>
    <p id="status">
    <span id="status_text"></span>
    </p>
    <script type="text/javascript" src="_static/get_meta.js" charset="utf-8"></script>


.. raw:: html

    <style>
    #twitter-widget-0 {
          width: 100% !important;
          height: 180px !important;
    }
    </style>
    <a class="twitter-timeline" Width="100%" height="200px" data-chrome="noborders nofooter transparent noscrollbar" href="https://twitter.com/mygeneinfo" data-widget-id="372882575196299264">Tweets by @mygeneinfo</a>
    <script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?'http':'https';if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src=p+"://platform.twitter.com/widgets.js";fjs.parentNode.insertBefore(js,fjs);}}(document,"script","twitter-wjs");</script>



What's new in v2 API
------------------------

* **ALL** species are supported now! That's more than 14,000 in total. [`more <doc/data.html#species>`_]
* Gene annotation data are even more `up-to-date <doc/data.html#data-sources>`_ (weekly updates).
* Gene query service supports `"fields" parameter <doc/query_service.html#fields>`_ to return any fields. Previously, you need to call gene query service separately if you need more than gene symbols and names.
* Fine-tuned query algorithm to return relevant gene hits first.
* Our query backend is more scalable and extensible. Ready to expand more annotation data as we go.

`Migration guide from v1 to v2 API <doc/migration_from_v1.html>`_

Still want to stick with v1 API for a while? It's still there: `v1 API <http://mygene.info/v1/doc>`_, but annotation data there won't be updated any more.

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

See FAQ page here: http://mygene.info/faq/


Contact us
-------------------------

* help@mygene.info
* `@mygeneinfo <https://twitter.com/mygeneinfo>`_


.. raw:: html

    <div id="spacer" style="height:300px"></div>


.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
