Gene annotation service
***********************************

This page describes the reference for MyGene.info gene annotation web service. It's also recommended to try it live on our `interactive API page <http://mygene.info/v2/api>`_.

Service endpoint
=================
::

    http://mygene.info/v2/gene

GET request
==================

To obtain the gene annotation via our web service is as simple as calling this URL::

    http://mygene.info/v2/gene/<geneid>

**geneid** above can be either Entrez gene id ("1017") or Ensembl gene id ("ENSG00000123374").
By default, this will return the complete gene annotation object in JSON format. See `here <#returned-object>`_ for an example and :ref:`here <gene_object>` for more details.

.. hint::
    A retired Entrez Gene id works too if it is replaced by a new one, e.g., `245794 </v2/gene/245794>`_. But a "*terminated*" gene id will not return any hit.

Optionally, you can pass a "**fields**" parameter to return only the annotation you want (by filtering returned object fields)::

    http://mygene.info/v2/gene/1017?fields=name,symbol

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



Returned object
---------------

A GET request like this::

    http://mygene.info/v2/gene/1017

should return a gene object below:

.. container:: gene-object-containter

    .. include :: gene_object.json



Batch queries via POST
======================

Although making simple GET requests above to our gene query service is sufficient in most of use cases,
there are some cases you might find it's more efficient to make queries in a batch (e.g., retrieving gene
annotation for multiple genes). Fortunately, you can also make batch queries via POST requests when you
need::


    URL: http://mygene.info/v2/gene
    HTTP method:  POST


Query parameters
----------------

ids
"""""
    Required. Accept multiple geneids (either Entrez or Ensembl gene ids) seperated by comma, e.g., 'ids=1017,1018' or 'ids=695,ENSG00000123374'. Note that currently we only take the input ids up to **1000** maximum, the rest will be omitted.

fields
"""""""
    Optional, can be a comma-separated fields to limit the fields returned from the matching hits.
    If “fields=all”, all available fields will be returned. Note that it supports dot notation as well, e.g., you can pass "refseq.rna". Default: “symbol,name,taxid,entrezgene,ensemblgene”.

species
"""""""""""
     Optional, can be used to limit the gene hits from given species. You can use "common names" for nine common species (human, mouse, rat, fruitfly, nematode, zebrafish, thale-cress, frog and pig). All other species, you can provide their taxonomy ids. See `more details here <data.html#species>`_. Multiple species can be passed using comma as a separator. Default: human,mouse,rat.

Example code
------------

Unlike GET requests, you can easily test them from browser, make a POST request is often done via a
piece of code, still trivial of course. Here is a sample python snippet::

    import httplib2
    h = httplib2.Http()
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    params = 'ids=1017,695&fields=name,symbol,refseq.rna'
    res, con = h.request('http://mygene.info/v2/gene', 'POST', params, headers=headers)

Returned object
---------------

Returned result (the value of "con" variable above) from above example code should look like this:

.. code-block:: json

    [
        {
         "refseq":
            {
                "rna": ["NM_001798.3",
                        "NM_052827.2"]
            },
         "symbol": "CDK2",
         "_id": "1017",
         "name": "cyclin-dependent kinase 2"
        },
        {
         "refseq":
            {
                "rna": "NM_000061.2"
            },
         "symbol": "BTK",
         "_id": "695",
         "name": "Bruton agammaglobulinemia tyrosine kinase"
        }
    ]





.. raw:: html

    <div id="spacer" style="height:300px"></div>