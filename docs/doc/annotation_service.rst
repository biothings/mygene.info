Gene annotation service
***********************************

This page describes the reference for MyGene.info gene annotation web service. It's also recommended to try it live on our `interactive API page <http://mygene.info/v3/api>`_.

Service endpoint
=================
::

    http://mygene.info/v3/gene

GET request
==================

To obtain the gene annotation via our web service is as simple as calling this URL::

    http://mygene.info/v3/gene/<geneid>

**geneid** above can be either Entrez gene id ("1017") or Ensembl gene id ("ENSG00000123374").
By default, this will return the complete gene annotation object in JSON format. See `here <#returned-object>`_ for an example and :ref:`here <gene_object>` for more details. If the input **geneid** is not valid, 404 (NOT FOUND) will be returned.

.. hint::
    A retired Entrez gene id works too if it is replaced by a new one, e.g., `245794 <http://mygene.info/v3/gene/245794>`_. But a "*discontinued*" gene id will not return any hit, e.g., `138 <http://www.ncbi.nlm.nih.gov/gene/138>`_.

Optionally, you can pass a "**fields**" parameter to return only the annotation you want (by filtering returned object fields)::

    http://mygene.info/v3/gene/1017?fields=name,symbol

"**fields**" accepts any attributes (a.k.a fields) available from the gene object. Multiple attributes should be seperated by commas. If an attribute is not available for a specific gene object, it will be ignored. Note that the attribute names are case-sensitive.

Just like `gene query service <query_service.html>`_, you can also pass a "**callback**" parameter to make a `JSONP <http://ajaxian.com/archives/jsonp-json-with-padding>`_ call.



Query parameters
-----------------

fields
""""""""
    Optional, can be a comma-separated fields to limit the fields returned from the gene object. If "fields=all", all available fields will be returned. Note that it supports dot notation as well, e.g., you can pass "refseq.rna". Default: "fields=all".

callback
"""""""""
    Optional, you can pass a "**callback**" parameter to make a `JSONP <http://ajaxian.com/archives/jsonp-json-with-padding>` call.

filter
"""""""
    Alias for "fields" parameter.

dotfield
""""""""""
    Optional, can be used to control the format of the returned fields when passed "fields" parameter contains dot notation, e.g. "fields=refseq.rna". If "dofield" is true, the returned data object contains a single "refseq.rna" field, otherwise, a single "refseq" field with a sub-field of "rna". Default: false.

email
""""""
    Optional, if you are regular users of our services, we encourage you to provide us an email, so that we can better track the usage or follow up with you.


Returned object
---------------

A GET request like this::

    http://mygene.info/v3/gene/1017

should return a gene object below:

.. container:: gene-object-containter

    .. include :: gene_object.json



Batch queries via POST
======================

Although making simple GET requests above to our gene query service is sufficient in most of use cases,
there are some cases you might find it's more efficient to make queries in a batch (e.g., retrieving gene
annotation for multiple genes). Fortunately, you can also make batch queries via POST requests when you
need::


    URL: http://mygene.info/v3/gene
    HTTP method:  POST


Query parameters
----------------

ids
"""""
    Required. Accept multiple geneids (either Entrez or Ensembl gene ids) seperated by comma, e.g., 'ids=1017,1018' or 'ids=695,ENSG00000123374'. Note that currently we only take the input ids up to **1000** maximum, the rest will be omitted.

fields
"""""""
    Optional, can be a comma-separated fields to limit the fields returned from the matching hits.
    If “fields=all”, all available fields will be returned. Note that it supports dot notation as well, e.g., you can pass "refseq.rna". Default: “symbol,name,taxid,entrezgene”.

species
"""""""""""
    Optional, can be used to limit the gene hits from given species. You can use "common names" for nine common species (human, mouse, rat, fruitfly, nematode, zebrafish, thale-cress, frog and pig). All other species, you can provide their taxonomy ids. See `more details here <data.html#species>`_. Multiple species can be passed using comma as a separator. Passing "all" will query against all available species. Default: all.

dotfield
""""""""""
    Optional, can be used to control the format of the returned fields when passed "fields" parameter contains dot notation, e.g. "fields=refseq.rna". If "dofield" is true, the returned data object contains a single "refseq.rna" field, otherwise, a single "refseq" field with a sub-field of "rna". Default: false.

email
""""""
    Optional, if you are regular users of our services, we encourage you to provide us an email, so that we can better track the usage or follow up with you.

Example code
------------

Unlike GET requests, you can easily test them from browser, make a POST request is often done via a
piece of code, still trivial of course. Here is a sample python snippet::

    import requests
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    params = 'ids=1017,695&fields=name,symbol,refseq.rna'
    res = requests.post('http://mygene.info/v3/gene', data=params, headers=headers)

Returned object
---------------

Returned result (the value of "res.text" variable above) from above example code should look like this:

.. code-block:: json

    [
      {
        '_id': '1017',
        '_score': 21.731894,
        'name': 'cyclin dependent kinase 2',
        'query': '1017',
        'refseq': {
          'rna': [
            'NM_001290230.1',
            'NM_001798.4',
            'NM_052827.3',
            'XM_011537732.1'
          ]
        },
        'symbol': 'CDK2'
      },
      {
        '_id': '695',
        '_score': 21.730501,
        'name': 'Bruton tyrosine kinase',
        'query': '695',
        'refseq': {
          'rna': [
            'NM_000061.2',
            'NM_001287344.1',
            'NM_001287345.1'
          ]
        },
        'symbol': 'BTK'
      }
    ]




.. raw:: html

    <div id="spacer" style="height:300px"></div>
