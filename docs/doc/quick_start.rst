Quick start
-----------

`MyGene.info <http://mygene.info>`_ provides two simple web services: one for gene queries and the other for gene annotation retrieval. Both return results in `JSON <http://json.org>`_ format.

Gene query service
^^^^^^^^^^^^^^^^^^


URL
"""""
::

    http://mygene.info/v3/query

Examples
""""""""
::

    http://mygene.info/v3/query?q=cdk2
    http://mygene.info/v3/query?q=cdk2&species=human
    http://mygene.info/v3/query?q=cdk?
    http://mygene.info/v3/query?q=IL*
    http://mygene.info/v3/query?q=entrezgene:1017
    http://mygene.info/v3/query?q=ensemblgene:ENSG00000123374
    http://mygene.info/v3/query?q=cdk2&fields=symbol,refseq

.. Hint:: View nicely formatted JSON result in your browser with this handy add-on: `JSON formater <https://chrome.google.com/webstore/detail/bcjindcccaagfpapjjmafapmmgkkhgoa>`_ for Chrome or `JSONView <https://addons.mozilla.org/en-US/firefox/addon/jsonview/>`_ for Firefox.



To learn more
"""""""""""""

* You can read `the full description of our query syntax here <doc/query_service.html>`__.
* Try it live on `interactive API page <http://mygene.info/v3/api>`_.
* Play with our `demo applications <doc/usage_demo.html#demo>`_.
* Batch queries? Yes, you can. do it with `a POST request <doc/query_service.html#batch-queries-via-post>`_.



Gene annotation service
^^^^^^^^^^^^^^^^^^^^^^^

URL
"""""
::

    http://mygene.info/v3/gene/<geneid>

Examples
""""""""
::

    http://mygene.info/v3/gene/1017
    http://mygene.info/v3/gene/ENSG00000123374
    http://mygene.info/v3/gene/1017?fields=name,symbol,summary

"*\<geneid\>*" can be any of valid Entrez or Ensembl Gene ids. A retired Entrez Gene id works too if it is replaced by a new one.


To learn more
"""""""""""""

* You can read `the full description of our query syntax here <doc/annotation_service.html>`__.
* Try it live on `interactive API page <http://mygene.info/v3/api>`_.
* Play with our `demo applications <doc/usage_demo.html#demo>`_.
* Yes, batch queries via `POST request <doc/annotation_service.html#batch-queries-via-post>`_ as well.
