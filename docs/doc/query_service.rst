Gene query service
******************************

.. role:: raw-html(raw)
   :format: html
.. |info| image:: /_static/information.png
             :alt: information!


This page describes the reference for MyGene.info gene query web service. It's also recommended to try it live on our `interactive API page <http://mygene.info/v3/api>`_.


Service endpoint
=================

::

    http://mygene.info/v3/query

GET request
==================

Query parameters
-----------------

q
"""""
    Required, passing user query. The detailed query syntax for parameter "**q**" we explained `below <#query-syntax>`_.

fields
""""""
    Optional, can be a comma-separated fields to limit the fields returned from the matching gene hits. The supported field names can be found from any gene object (e.g. `gene 1017 <http://mygene.info/v3/gene/1017>`_). Note that it supports dot notation as well, e.g., you can pass "refseq.rna". If "fields=all", all available fields will be returned. Default:
    "symbol,name,taxid,entrezgene".

species
"""""""
    Optional, can be used to limit the gene hits from given species. You can use "common names" for nine common species (human, mouse, rat, fruitfly, nematode, zebrafish, thale-cress, frog and pig). All other species, you can provide their taxonomy ids. See `more details here <data.html#species>`_. Multiple species can be passed using comma as a separator. Passing "all" will query against all available species. Default: all.

size
""""
    Optional, the maximum number of matching gene hits to return (with a cap of 1000 at the moment). Default: 10.

from
""""
    Optional, the number of matching gene hits to skip, starting from 0. Default: 0

.. Hint:: The combination of "**size**" and "**from**" parameters can be used to get paging for large query:

::

    q=cdk*&size=50                     first 50 hits
    q=cdk*&size=50&from=50             the next 50 hits

sort
""""
    Optional, the comma-separated fields to sort on. Prefix with "-" for descending order, otherwise in ascending order. Default: sort by matching scores in decending order.

facets
""""""
    Optional, a single field or comma-separated fields to return facets, for example, "facets=taxid", "facets=taxid,type_of_gene". See `examples of faceted queries here <#faceted-queries>`_.

species_facet_filter
""""""""""""""""""""
    Optional, relevant when faceting on species (i.e., "facets=taxid" are passed). It's used to pass species filter without changing the scope of faceting, so that the returned facet counts won't change. Either species name or taxonomy id can be used, just like "`species <#species>`_" parameter above. See `examples of faceted queries here <#faceted-queries>`_.

entrezonly
""""""""""
    Optional, when passed as "true" or "1", the query returns only the hits with valid Entrez gene ids. Default: false.

ensemblonly
"""""""""""
    Optional, when passed as "true" or "1", the query returns only the hits with valid Ensembl gene ids. Default: false.

callback
""""""""
    Optional, you can pass a "**callback**" parameter to make a `JSONP <http://ajaxian.com/archives/jsonp-json-with-padding>`_ call.

dotfield
""""""""""
    Optional, can be used to control the format of the returned fields when passed "fields" parameter contains dot notation, e.g. "fields=refseq.rna". If "dofield" is true, the returned data object contains a single "refseq.rna" field, otherwise, a single "refseq" field with a sub-field of "rna". Default: false.

filter
""""""
    Alias for "fields" parameter.

limit
"""""
    Alias for "size" parameter.

skip
""""
    Alias for "from" parameter.

email
""""""
    Optional, if you are regular users of our services, we encourage you to provide us an email, so that we can better track the usage or follow up with you.


Query syntax
------------
Examples of query parameter "**q**":


Simple queries
""""""""""""""

search for everything::

    q=cdk2                              search for any fields
    q=tumor suppressor                  default as "AND" for all query terms
    q="cyclin-dependent kinase"         search for the phrase



Fielded queries
"""""""""""""""
::

    q=entrezgene:1017
    q=symbol:cdk2
    q=refseq:NM_001798


.. _available_fields:

Available fields
^^^^^^^^^^^^^^^^

This table lists some commonly used fields can be used for "fielded queries". `Check here <./data.html#available-fields>`_ for the complete list of available fields.

========================    =============================================    =================================================================================
Field                        Description                                     Examples
========================    =============================================    =================================================================================
**entrezgene**                Entrez gene id                                    `q=entrezgene:1017 <http://mygene.info/v3/query?q=entrezgene:1017>`_
**ensembl.gene**               Ensembl gene id                                   `q=ensembl.gene:ENSG00000123374 <http://mygene.info/v3/query?q=ensembl.gene:ENSG00000123374>`_
**symbol**                    official gene symbol                              `q=symbol:cdk2 <http://mygene.info/v3/query?q=symbol:cdk2>`_
**name**                      gene name                                         `q=name:cyclin-dependent <http://mygene.info/v3/query?q=name:cyclin-dependent>`_
**alias**                     gene alias                                        `q=alias:p33 <http://mygene.info/v3/query?q=alias:p33>`_
**summary**                   gene summary text                                 `q=summary:insulin <http://mygene.info/v3/query?q=summary:insulin>`_
**refseq**                    NCBI RefSeq id  (both rna and proteins)           `q=refseq:NM_001798 <http://mygene.info/v3/query?q=refseq:NM_001798>`_ :raw-html:`<br />`
                                                                                `q=refseq:NP_439892 <http://mygene.info/v3/query?q=refseq:NP_439892>`_
**unigene**                   NCBI UniGene id                                   `q=unigene:Hs.19192 <http://mygene.info/v3/query?q=unigene:Hs.19192>`_
**homologene**                NCBI HomoloGene id                                `q=homologene:74409 <http://mygene.info/v3/query?q=homologene:74409>`_
**accession**                 NCBI GeneBank Accession number                    `q=accession:AA810989 <http://mygene.info/v3/query?q=accession:AA810989>`_
**ensembl.transcript**         Ensembl transcript id                             `q=ensembl.transcript:ENST00000266970 <http://mygene.info/v3/query?q=ensembl.transcript:ENST00000266970>`_
**ensembl.protein**            Ensembl protein id                                `q=ensembl.protein:ENSP00000243067 <http://mygene.info/v3/query?q=ensembl.protein:ENSP00000243067>`_
**uniprot**                   UniProt id                                        `q=uniprot:P24941 <http://mygene.info/v3/query?q=uniprot:P24941>`_
**ipi** (deprecated!)         IPI id                                            `q=ipi:IPI00031681 <http://mygene.info/v3/query?q=ipi:IPI00031681>`_
**pdb**                       PDB id                                            `q=pdb:1AQ1 <http://mygene.info/v3/query?q=pdb:1AQ1>`_
**prosite**                   Prosite id                                        `q=prosite:PS50011 <http://mygene.info/v3/query?q=prosite:PS50011>`_
**pfam**                      PFam id                                           `q=pfam:PF00069 <http://mygene.info/v3/query?q=pfam:PF00069>`_
**interpro**                  InterPro id                                       `q=interpro:IPR008351 <http://mygene.info/v3/query?q=interpro:IPR008351>`_
**mim**                       OMIM id                                           `q=mim:116953 <http://mygene.info/v3/query?q=MIM:116953>`_
**pharmgkb**                  PharmGKB id                                       `q=pharmgkb:PA101 <http://mygene.info/v3/query?q=pharmgkb:PA101>`_
**reporter**                  Affymetrix probeset id                            `q=reporter:204252_at <http://mygene.info/v3/query?q=reporter:204252_at>`_
**reagent**                   GNF reagent id                                    `q=reagent:GNF282834 <http://mygene.info/v3/query?q=reagent:GNF282834>`_
**go**                        Gene Ontology id                                  `q=go:0000307 <http://mygene.info/v3/query?q=go:0000307>`_
**hgnc**                      HUGO Gene Nomenclature Committee                  `q=hgnc:1771 <http://mygene.info/v3/query?q=HGNC:1771>`_
**hprd**                      Human Protein Reference Database                  `q=hprd:00310 <http://mygene.info/v3/query?q=HPRD:00310>`_
**mgi**                       Mouse Genome Informatics                          `q=mgi:MGI\\\\:88339 <http://mygene.info/v3/query?q=mgi:MGI%5C%5C:88339>`_
**rgd**                       Rat Genome Database                               `q=rgd:620620 <http://mygene.info/v3/query?q=RGD:620620>`_
**flybase**                   A Database of Drosophila Genes & Genomes          `q=flybase:FBgn0004107&species=fruitfly <http://mygene.info/v3/query?q=FLYBASE:FBgn0004107&species=fruitfly>`_
**wormbase**                  C elegans and related nematodes database          `q=wormbase:WBGene00057218&species=31234 <http://mygene.info/v3/query?q=wormbase:WBGene00057218&species=31234>`_
**zfin**                      Zebrafish Information Network                     `q=zfin:ZDB-GENE-980526-104&species=zebrafish <http://mygene.info/v3/query?q=ZFIN:ZDB-GENE-980526-104&species=zebrafish>`_
**tair**                      Arabidopsis Information Resource                  `q=tair:AT3G48750&species=thale-cress <http://mygene.info/v3/query?q=TAIR:AT3G48750&species=thale-cress>`_
**xenbase**                 | Xenopus laevis and Xenopus tropicalis             `q=xenbase:XB-GENE-1001990&species=frog <http://mygene.info/v3/query?q=xenbase:XB-GENE-1001990&species=frog>`_
                            | biology and genomics resource
**mirbase**                 | database of published miRNA                       `q=mirbase:MI0017267 <http://mygene.info/v3/query?q=mirbase:MI0017267>`_
                            | sequences and annotation
**retired**                 | Retired Entrez gene id, including                 `q=retired:84999 <http://mygene.info/v3/query?q=retired:84999>`_
                            | those with replaced gene ids.
========================    =============================================    =================================================================================



Genome interval query
"""""""""""""""""""""

When we detect your query ("**q**" parameter) contains a genome interval pattern like this one::

    chrX:151,073,054-151,383,976

we will do the genome interval query for you. Besides above interval string, you also need to specify "*species*" parameter (with the default as human). These are all acceptted queries::

    q=chrX:151073054-151383976&species:9606
    q=chrX:151,073,054-151,383,976&species:human


.. Hint:: As you can see above, the genomic locations can include commas in it.

.. seealso::

   `Genome assembly information <data.html#genome-assemblies>`_



Wildcard queries
""""""""""""""""
Wildcard character "*" or "?" is supported in either simple queries or fielded queries::

    q=CDK?                              single character wildcard
    q=symbol:CDK?                       single character wildcard within "symbol" field
    q=IL*R                              multiple character wildcard

.. note:: Wildcard character can not be the first character. It will be ignored.


Boolean operators and grouping
""""""""""""""""""""""""""""""

You can use **AND**/**OR**/**NOT** boolean operators and grouping to form complicated queries::

    q=tumor AND suppressor                        AND operator
    q=CDK2 OR BTK                                 OR operator
    q="tumor suppressor" NOT receptor             NOT operator
    q=(interleukin OR insulin) AND receptor       the use of parentheses


Returned object
---------------

A GET request like this::

    http://mygene.info/v3/query?q=symbol:cdk2

should return hits as:

.. code-block:: json

    {
      "hits": [
        {
          "name": "cyclin-dependent kinase 2",
          "_score": 87.76775,
          "symbol": "CDK2",
          "taxid": 9606,
          "entrezgene": 1017,
          "_id": "1017"
        },
        {
          "name": "cyclin-dependent kinase 2",
          "_score": 79.480484,
          "symbol": "Cdk2",
          "taxid": 10090,
          "entrezgene": 12566,
          "_id": "12566"
        },
        {
          "name": "cyclin dependent kinase 2",
          "_score": 62.286797,
          "symbol": "Cdk2",
          "taxid": 10116,
          "entrezgene": 362817,
          "_id": "362817"
        }
      ],
      "total": 3,
      "max_score": 87.76775,
      "took": 4
    }


Faceted queries
----------------
If you need to perform a faceted query, you can pass an optional "`facets <#facets>`_" parameter. For example, if you want to get the facets on species, you can pass "facets=taxid":

A GET request like this::

    http://mygene.info/v3/query?q=cdk2&size=1&facets=taxid

should return hits as:

.. code-block:: json
    :emphasize-lines: 15-36

    {
      "hits":[
        {
          "entrezgene":1017,
          "name":"cyclin-dependent kinase 2",
          "_score":400.43347,
          "symbol":"CDK2",
          "_id":"1017",
          "taxid":9606
        }
      ],
      "total":26,
      "max_score":400.43347,
      "took":7,
      "facets":{
        "taxid":{
          "_type":"terms",
          "total":26,
          "terms":[
            {
              "count":14,
              "term":9606
            },
            {
              "count":7,
              "term":10116
            },
            {
              "count":5,
              "term":10090
            }
          ],
          "other":0,
          "missing":0
        }
      }
    }

Another useful field to get facets on is "type_of_gene"::

    http://mygene.info/v3/query?q=cdk2&size=1&facets=type_of_gene

It should return hits as:

.. code-block:: json
    :emphasize-lines: 15-32

    {
      "hits":[
        {
          "entrezgene":1017,
          "name":"cyclin-dependent kinase 2",
          "_score":400.43347,
          "symbol":"CDK2",
          "_id":"1017",
          "taxid":9606
        }
      ],
      "total":26,
      "max_score":400.43347,
      "took":97,
      "facets":{
        "type_of_gene":{
          "_type":"terms",
          "total":26,
          "terms":[
            {
              "count":20,
              "term":"protein-coding"
            },
            {
              "count":6,
              "term":"pseudo"
            }
          ],
          "other":0,
          "missing":0
        }
      }
    }

If you need to, you can also pass multiple fields as comma-separated list::

    http://mygene.info/v3/query?q=cdk2&size=1&facets=taxid,type_of_gene


Particularly relevant to species facets (i.e., "facets=taxid"), you can pass a
"`species_facet_filter <#species_facet_filter>`_" parameter to filter the returned hits on a given species, without changing the scope of the facets (i.e. facet counts will not change). This is useful when you need to get the subset of the hits for a given species after the initial faceted query on species.

You can see the different "hits" are returned in the following queries, while "facets" keeps the same::

    http://mygene.info/v3/query?q=cdk?&size=1&facets=taxid&species_facet_filter=human

v.s.
::

    http://mygene.info/v3/query?q=cdk?&size=1&facets=taxid&species_facet_filter=mouse





Batch queries via POST
======================

Although making simple GET requests above to our gene query service is sufficient in most of use cases,
there are some cases you might find it's more efficient to make queries in a batch (e.g., retrieving gene
annotation for multiple genes). Fortunately, you can also make batch queries via POST requests when you
need::


    URL: http://mygene.info/v3/query
    HTTP method:  POST


Query parameters
----------------

q
"""
    Required, multiple query terms seperated by comma (also support "+" or white space), but no wildcard, e.g., 'q=1017,1018' or 'q=CDK2+BTK'

scopes
""""""
    Optional, specify one or more fields (separated by comma) as the search "scopes", e.g., "scopes=entrezgene",
    "scopes=entrezgene,ensemblgene". The available "fields" can be passed to "**scopes**" parameter are
    :ref:`listed above <available_fields>`. Default: "scopes=entrezgene,ensemblgene,retired" (either Entrez
    or Ensembl gene ids).

species
"""""""
     Optional, can be used to limit the gene hits from given species. You can use "common names" for nine common species (human, mouse, rat, fruitfly, nematode, zebrafish, thale-cress, frog and pig). All other species, you can provide their taxonomy ids. See `more details here <data.html#species>`_. Multiple species can be passed using comma as a separator. Default: all.

fields
""""""
    Optional, can be a comma-separated fields to limit the fields returned from the matching gene hits. The supported field names can be found from any gene object (e.g. `gene 1017 <http://mygene.info/v3/gene/1017>`_). Note that it supports dot notation as well, e.g., you can pass "refseq.rna". If "fields=all", all available fields will be returned. Default:
    "symbol,name,taxid,entrezgene".

dotfield
""""""""""
    Optional, can be used to control the format of the returned fields when passed "fields" parameter contains dot notation, e.g. "fields=refseq.rna". If "dofield" is true, the returned data object contains a single "refseq.rna" field, otherwise, a single "refseq" field with a sub-field of "rna". Default: false.

email
""""""
    Optional, if you are regular users of our services, we encourage you to provide us an email, so that we can better track the usage or follow up with you.

Example code
------------

Unlike GET requests, you can easily test them from browser, make a POST request is often done via a
piece of code. Here is a sample python snippet::

    import requests
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    params = 'q=1017,1018&scopes=entrezgene&fields=name,symbol,taxid,entrezgene'
    res = requests.post('http://mygene.info/v3/query', data=params, headers=headers)


Returned object
---------------

Returned result (the value of "res.text" variable above) from above example code should look like this:

.. code-block:: json

    [
      {
        '_id': '1017',
        '_score': 22.757837,
        'entrezgene': 1017,
        'name': 'cyclin dependent kinase 2',
        'query': '1017',
        'symbol': 'CDK2',
        'taxid': 9606
      },
      {
        '_id': '1018',
        '_score': 22.757782,
        'entrezgene': 1018,
        'name': 'cyclin dependent kinase 3',
        'query': '1018',
        'symbol': 'CDK3',
        'taxid': 9606
      }
    ]


.. Tip:: "query" field in returned object indicates the matching query term.
.. Note:: if no "fields" parameter is specified, all available fields will be returned

If a query term has no match, it will return with "**notfound**" field as "**true**"::

    params = 'q=1017,dummy&scopes=entrezgene&fields=name,symbol,taxid,entrezgene'
    res = requests.post('http://mygene.info/v3/query', data=params, headers=headers)

.. code-block:: json
    :emphasize-lines: 12

    [
      {
        "name": "cyclin-dependent kinase 2",
        "symbol": "CDK2",
        "taxid": 9606,
        "entrezgene": 1017,
        "query": "1017",
        "_id": "1017"
      },
      {
        "query": "dummy",
        "notfound": true
      }
    ]

If a query term has multiple matches, they will be included with the same "query" field::

    params = 'q=tp53,1017&scopes=symbol,entrezgene&fields=name,symbol,taxid,entrezgene'
    res = requests.post('http://mygene.info/v3/query', data=params, headers=headers)


.. code-block:: json
    :emphasize-lines: 7,15

    [
      {
        "name": "tumor protein p53",
        "symbol": "TP53",
        "taxid": 9606,
        "entrezgene": 7157,
        "query": "tp53",
        "_id": "7157"
      },
      {
        "name": "tumor protein p53",
        "symbol": "Tp53",
        "taxid": 10116,
        "entrezgene": 24842,
        "query": "tp53",
        "_id": "24842"
      },
      {
        "name": "cyclin-dependent kinase 2",
        "symbol": "CDK2",
        "taxid": 9606,
        "entrezgene": 1017,
        "query": "1017",
        "_id": "1017"
      }
    ]







.. raw:: html

    <div id="spacer" style="height:300px"></div>
