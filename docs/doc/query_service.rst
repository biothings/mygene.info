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
    Optional, can be a comma-separated fields to limit the fields returned from the matching gene hits. The supported field names can be found from any gene object (e.g. `gene 1017 <http://mygene.info/v3/gene/1017>`_). Note that it supports dot notation as well, e.g., you can pass "refseq.rna". If "fields=all", all available fields will be returned. To leave fields out instead, prefix them with "-", e.g., "fields=-go,-pathway" returns all fields except "go" and "pathway". Default:
    "symbol,name,taxid,entrezgene".

species
"""""""
    Optional, can be used to limit the gene hits from given species. You can use "common names" for nine common species (human, mouse, rat, fruitfly, nematode, zebrafish, thale-cress, frog and pig). All other species, you can provide their taxonomy ids. See `more details here <data.html#species>`_. Multiple species can be passed using comma as a separator. Passing "all" will query against all available species. Default: all.

include_tax_tree
""""""""""""""""
    Optional, when passed as "true" or "1", the "**species**" parameter also matches all the taxa under each given species or taxon in the NCBI taxonomy, e.g., "species=9605&include_tax_tree=true" returns hits from every species of the genus *Homo* (taxonomy id 9605), including human. Default: false.

size
""""
    Optional, the maximum number of matching gene hits to return (with a cap of 1000 at the moment). Default: 10.

from
""""
    Optional, the number of matching gene hits to skip, starting from 0. "**from**" + "**size**" can be at most 10,000; to get the hits beyond that, use `search_after <#search-after>`__ (GET only). Default: 0

.. Hint:: The combination of "**size**" and "**from**" parameters can be used to get paging for large query:

::

    q=cdk*&size=50                     first 50 hits
    q=cdk*&size=50&from=50             the next 50 hits

search_after
""""""""""""
    Optional, used to page through all hits of a query, including beyond the first 10,000 that **size** and **from** can reach.  Pass **search_after** = ``*`` with the first request.  While more hits remain, the response contains a **_search_after** field.  Send the same query again with **search_after** set to that value to get the next page, until a response no longer contains **_search_after**.  Unlike **fetch_all**, the hits can be sorted with the **sort** parameter.  Each page returns **size** hits (1000 by default), and a **_search_after** value expires 1 minute after the page it came with.  It cannot be combined with **from**, **facets**, **fetch_all** or **scroll_id**.  For more information see `examples using search_after here <#paging-with-search-after>`_.

fetch_all
"""""""""
    Deprecated, use `search_after <#search-after>`__ instead.  Optional, a boolean, which when TRUE, allows fast retrieval of all unsorted query hits.  The return object contains a **_scroll_id** field, which when passed as a parameter to the query endpoint, returns the next 1000 query results.  Setting **fetch_all** = TRUE causes the results to be inherently unsorted, therefore the **sort** parameter is ignored.  For more information see `examples using fetch_all here <#scrolling-queries>`_.  Default: FALSE.

scroll_id
"""""""""
    Deprecated, use `search_after <#search-after>`__ instead.  Optional, a string containing the **_scroll_id** returned from a query request with **fetch_all** = TRUE.  Supplying a valid **scroll_id** will return the next 1000 unordered results.  If the next results are not obtained within 1 minute of the previous set of results, the **scroll_id** becomes stale, and a new one must be obtained with another query request with **fetch_all** = TRUE.  All other parameters are ignored when the **scroll_id** parameter is supplied.  For more information see `examples using scroll_id here <#scrolling-queries>`_.

sort
""""
    Optional, the comma-separated fields to sort on. Prefix with "-" for descending order, otherwise in ascending order. Default: sort by matching scores in descending order.

facets
""""""
    Optional, a single field or comma-separated fields to return facets, for example, "facets=taxid", "facets=taxid,type_of_gene". See `examples of faceted queries here <#faceted-queries>`_.

facet_size
""""""""""
    Optional, an integer (1 <= **facet_size** <= 1000) that specifies how many buckets to return in a faceted query.

species_facet_filter
""""""""""""""""""""
    Optional, relevant when faceting on species (i.e., "facets=taxid" are passed). It's used to pass species filter without changing the scope of faceting, so that the returned facet counts won't change. Either species name or taxonomy id can be used, just like "`species <#species>`_" parameter above. See `examples of faceted queries here <#faceted-queries>`_.

entrezonly
""""""""""
    Optional, when passed as "true" or "1", the query returns only the hits with valid Entrez gene ids. Default: false.

ensemblonly
"""""""""""
    Optional, when passed as "true" or "1", the query returns only the hits with valid Ensembl gene ids. Default: false.

exists
""""""
    Optional, a comma-separated list of fields. The query returns only the hits that have all of these fields, e.g., "exists=pathway.kegg" returns only the genes with KEGG pathways.

missing
"""""""
    Optional, a comma-separated list of fields. The query returns only the hits that have none of these fields, e.g., "missing=ensembl" returns only the genes without Ensembl gene ids.

filter
""""""
    Optional, a query in the Elasticsearch `query string syntax <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html#query-string-syntax>`_ that the hits must also match, e.g., "filter=taxid:9606" or "filter=type_of_gene:protein-coding". Unlike adding it to "**q**", it doesn't change the scores of the hits. The facet counts only include the hits that match it. It takes full field names, e.g., "filter=refseq.rna:NM_001798": the shortcuts in `Available fields <#available-fields>`__, like "refseq" and "uniprot", only work in "**q**". Note that "**filter**" used to be an alias for "**fields**"; use "**fields**" for that.

post_filter
"""""""""""
    Optional, like "**filter**", but applied after the facets are counted, so it narrows down the hits without changing the facet counts, e.g., "facets=taxid&post_filter=type_of_gene:protein-coding". "`species_facet_filter <#species-facet-filter>`__" does the same for species.

dotfield
""""""""
    Optional, can be used to control the format of the returned gene object.  If "dotfield" is true, the returned data object is returned flattened (no nested objects) using dotfield notation for key names.  Default: false.

always_list
"""""""""""
    Optional, a comma-separated list of fields to always return as lists, even when a gene has a single value for them, e.g., with "fields=symbol,ensembl.gene&always_list=ensembl", "ensembl" is a list even for a gene with one Ensembl gene.

allow_null
""""""""""
    Optional, a comma-separated list of fields to include in every hit, as null when a gene doesn't have them, e.g., "fields=symbol,pharmgkb&allow_null=pharmgkb". A dotted field, like "refseq.rna", is only added to the hits that have its parent, "refseq".

jmespath
""""""""
    Optional, transforms a field of each hit with a `JMESPath <https://jmespath.org>`_ expression, passed as ``<field>|<expression>``. For example, ``fields=go.BP&jmespath=go.BP|[?evidence=='IDA'].term`` replaces each gene's "go.BP" with the names of its terms that have IDA evidence.

jmespath_exclude_empty
""""""""""""""""""""""
    Optional, when passed as "true" or "1", leaves out the hits whose field is empty after the "**jmespath**" transformation. The total number of hits doesn't change, so a page can have fewer hits than "**size**". Default: false.

format
""""""
    Optional, the format of the response: "json", "yaml", "html" (the JSON in a web page) or "msgpack". Default: json.

explain
"""""""
    Optional, when passed as "true" or "1", each hit includes an "**_explanation**" field with Elasticsearch's breakdown of its score.

rawquery
""""""""
    Optional, when passed as "true" or "1", returns the Elasticsearch query built for your request instead of running it.

raw
"""
    Optional, when passed as "true" or "1", returns the Elasticsearch response as is, without formatting the hits.

limit
"""""
    Alias for "size" parameter.

skip
""""
    Alias for "from" parameter.


Query syntax
------------
Examples of query parameter "**q**":


Simple queries
""""""""""""""

search for everything::

    q=cdk2                              search for any fields
    q=tumor suppressor                  default as "AND" for all query terms
    q="cyclin-dependent kinase"         search for the phrase
    q=__all__                           all genes; with "facets" and no "size", only the facet counts



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
**prev_symbol**               former official gene symbol (human, HGNC)         `q=prev_symbol:PARK2 <http://mygene.info/v3/query?q=prev_symbol:PARK2>`_
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
**mgi**                       Mouse Genome Informatics                          `q=mgi:MGI\\:88339 <http://mygene.info/v3/query?q=mgi:MGI%5C:88339>`_
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

we will do the genome interval query for you. Pass the "*species*" parameter too: without it, the query returns the genes of every species with a matching chromosome and range. These are all accepted queries::

    q=chrX:151073054-151383976&species=9606
    q=chrX:151,073,054-151,383,976&species=human

The query uses the current genome assembly of each species. For human and mouse, you can also search the older hg19 and mm9 assemblies by adding "hg19." or "mm9." before the interval::

    q=hg19.chr12:56360553-56366568&species=human
    q=mm9.chr10:128134995-128142107&species=mouse


.. Hint:: As you can see above, the genomic locations can include commas in it.

.. seealso::

   `Genome assembly information <data.html#genome-assemblies>`_



Wildcard queries
""""""""""""""""
Wildcard character "*" or "?" is supported in either simple queries or fielded queries::

    q=CDK?                              single character wildcard
    q=symbol:CDK?                       single character wildcard within "symbol" field
    q=IL*R                              multiple character wildcard
    q=*DK2                              wildcard as the first character


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
"`species_facet_filter <#species-facet-filter>`_" parameter to filter the returned hits on a given species, without changing the scope of the facets (i.e. facet counts will not change). This is useful when you need to get the subset of the hits for a given species after the initial faceted query on species.

You can see the different "hits" are returned in the following queries, while "facets" keeps the same::

    http://mygene.info/v3/query?q=cdk?&size=1&facets=taxid&species_facet_filter=human

v.s.
::

    http://mygene.info/v3/query?q=cdk?&size=1&facets=taxid&species_facet_filter=mouse


Paging with search_after
------------------------
If you want to return ALL results of a very large query, including beyond the first 10,000 results that the paging method described `above <#from>`__ can reach, page through them with **search_after**.  To begin, call the query endpoint as you normally would, but with an extra parameter **search_after** = ``*``.  For example, a GET request to::

    http://mygene.info/v3/query?q=brain&fields=symbol,name&size=1000&search_after=*

Returns an object like this:

.. code-block:: json
    :force:

    {
      "took": 31,
      "_search_after": "eyJwaXQiOiI0OFAxQkFFSWJYbG5aVzVsWDJOMWNuSmxiblFX...",
      "total": 14571,
      "max_score": null,
      "hits": [
        {
          "_id": "...",
          "_score": null,
          "name": "...",
          "symbol": "..."
        },
        .
        .
        .
      ]
    }

To get the next page, send the same query again, with **search_after** set to the **_search_after** value of the previous response::

    http://mygene.info/v3/query?q=brain&fields=symbol,name&size=1000&search_after=eyJwaXQiOiI0OFAxQkFFSWJYbG5aVzVsWDJOMWNuSmxiblFX...

Repeat this until a response no longer contains **_search_after**, which means it is the last page.  Each request must repeat the parameters of the first one that select and order the hits, like **q**, **sort**, **species** and the filters, otherwise it returns an error.  The **fields** and **size** parameters can change between pages.

Without a **sort** parameter, the hits are returned in index order, the fastest order to page through, and their **_score** is null.  With **sort**, the hits are sorted across all the pages, for example::

    http://mygene.info/v3/query?q=brain&fields=symbol,name&size=1000&sort=symbol&search_after=*

.. Hint:: A **_search_after** value remains valid for 1 minute after the page it came with, and each page starts a new minute.  If it expires before you get the last page, start again with **search_after** = ``*``.


Scrolling queries
-----------------
.. note:: Scrolling queries are deprecated, use `search_after <#paging-with-search-after>`__ instead, the deep pagination Elasticsearch recommends.  Scrolling still works, and its responses include a **_warning** field recommending **search_after**.

If you want to return ALL results of a very large query (>10,000 results), sometimes the paging method described `above <#from>`_ can take too long.  In these cases, you can use a scrolling query.
This is a two-step process that turns off database sorting to allow very fast retrieval of all query results.  To begin a scrolling query, you first call the query
endpoint as you normally would, but with an extra parameter **fetch_all** = TRUE.  For example, a GET request to::

    http://mygene.info/v3/query?q=brain&fetch_all=TRUE

Returns the following object:

.. code-block:: json

    {
      "_scroll_id": "cXVlcnlUaGVuRmV0Y2g7MTA7MjA1NjY1MzMwOl9HM29rRkg2VFZ5S1c3cTJtYkI4RHc7MjA1NjY1MjY3OlM0V1VCa194UWdLYjlQWTR5NGZCeFE7MjA1NjY1MTM0OlRGWVpXLVZrU2NTWmZLQUlEVnlRRkE7MjA1NjY1MzMxOl9HM29rRkg2VFZ5S1c3cTJtYkI4RHc7MzEyMDY0NzU6TVBZd0FEVF9UcVdSQWhWajlfN2U4ZzsyMDU2NjUxMzM6VEZZWlctVmtTY1NaZktBSURWeVFGQTsyMDU2NjUxMzU6VEZZWlctVmtTY1NaZktBSURWeVFGQTsyMDU2NjUzMzI6X0czb2tGSDZUVnlLVzdxMm1iQjhEdzsyMDU2NjUyNjg6UzRXVUJrX3hRZ0tiOVBZNHk0ZkJ4UTszMTIwNjQ3NDpNUFl3QURUX1RxV1JBaFZqOV83ZThnOzA7",
      "max_score": 13.958638,
      "took": 270,
      "total": 14571,
      "hits": [
        {
          "_id": "390259",
          "_score": 13.958638,
          "entrezgene": 390259,
          "name": "brain specific homeobox",
          "symbol": "BSX",
          "taxid": 9606
        },
        .
        .
        .
      ]
    }

At this point, the first 1000 hits have been returned (of ~14,000 total), and a scroll has been set up for your query.  To get the next batch of 1000 unordered results, simply execute a GET request to the following address, supplying the _scroll_id from the first step into the **scroll_id** parameter in the second step::

    http://mygene.info/v3/query?scroll_id=cXVlcnlUaGVuRmV0Y2g7MTA7MjA1NjY1MzMwOl9HM29rRkg2VFZ5S1c3cTJtYkI4RHc7MjA1NjY1MjY3OlM0V1VCa194UWdLYjlQWTR5NGZCeFE7MjA1NjY1MTM0OlRGWVpXLVZrU2NTWmZLQUlEVnlRRkE7MjA1NjY1MzMxOl9HM29rRkg2VFZ5S1c3cTJtYkI4RHc7MzEyMDY0NzU6TVBZd0FEVF9UcVdSQWhWajlfN2U4ZzsyMDU2NjUxMzM6VEZZWlctVmtTY1NaZktBSURWeVFGQTsyMDU2NjUxMzU6VEZZWlctVmtTY1NaZktBSURWeVFGQTsyMDU2NjUzMzI6X0czb2tGSDZUVnlLVzdxMm1iQjhEdzsyMDU2NjUyNjg6UzRXVUJrX3hRZ0tiOVBZNHk0ZkJ4UTszMTIwNjQ3NDpNUFl3QURUX1RxV1JBaFZqOV83ZThnOzA7

.. Hint:: Your scroll will remain active for 1 minute from the last time you requested results from it.  If your scroll expires before you get the last batch of results, you must re-request the scroll_id by setting **fetch_all** = TRUE as in step 1.


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
    Required, multiple query terms separated by comma (also "+", "|" or white space), but no wildcard, e.g., ``q=1017,1018`` or ``q=CDK2+BTK``. Put a term in double quotes to keep the white space in it, e.g., ``q="cyclin dependent kinase 2",BTK``. "**q**" can also be a JSON list, e.g., ``q=["1017","CDK2"]``, and each query term can be a list of values that match several fields at once, see `compound queries <#compound-queries>`__.
    Note that currently we only take the input query terms up to **5000** maximum. Passing more than 5000 terms returns an HTTP 400 error.

scopes
""""""
    Optional, specify one or more fields (separated by comma) as the search "scopes", e.g., "scopes=entrezgene",
    "scopes=entrezgene,ensemblgene". The available "fields" can be passed to "**scopes**" parameter are
    :ref:`listed above <available_fields>`. Default: "scopes=_id,entrezgene,ensembl.gene,retired" (Entrez
    or Ensembl gene ids, including retired Entrez gene ids). To look up gene symbols, use "scopes=symbol". It also matches former official
    symbols, such as "PARK2" for "PRKN", ranked the same way as in a GET query. Add "alias" to match other
    synonyms too. For `compound queries <#compound-queries>`__, pass one field, or a list of fields, for
    each value of a query term.

species
"""""""
     Optional, can be used to limit the gene hits from given species. You can use "common names" for nine common species (human, mouse, rat, fruitfly, nematode, zebrafish, thale-cress, frog and pig). All other species, you can provide their taxonomy ids. See `more details here <data.html#species>`_. Multiple species can be passed using comma as a separator. Default: all.

fields
""""""
    Optional, can be a comma-separated fields to limit the fields returned from the matching gene hits. The supported field names can be found from any gene object (e.g. `gene 1017 <http://mygene.info/v3/gene/1017>`_). Note that it supports dot notation as well, e.g., you can pass "refseq.rna". If "fields=all", all available fields will be returned. Default:
    "symbol,name,taxid,entrezgene".

size
""""
    Optional, the maximum number of hits to return for each query term (with a cap of 1000). Default: 10. The number of query terms times "**size**" can be at most 100,000; a request asking for more returns an HTTP 400 error.

dotfield
""""""""""
    Optional, can be used to control the format of the returned fields when passed "fields" parameter contains dot notation, e.g. "fields=refseq.rna". If "dotfield" is true, the returned data object contains a single "refseq.rna" field, otherwise, a single "refseq" field with a sub-field of "rna". Default: false.

with_total
""""""""""
    Optional, when passed as "true" or "1", the response is an object instead of a list: the hits are in "**hits**", the largest number of hits that any query term matched, counted up to 10,000, is in "**max_total**", and if some query terms matched more hits than "**size**", "**msg**" says how many. See the :ref:`example below <with_total_example>`. Default: false.

analyzer
""""""""
    Optional, the name of an Elasticsearch analyzer, such as the `built-in <https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-analyzers.html>`_ "standard", to analyze the query terms with, instead of the analyzer of each field in "**scopes**". An unknown name returns an error.

Other parameters
""""""""""""""""
    POST queries also take these GET parameters: `from <#from>`__, `sort <#sort>`__, `entrezonly <#entrezonly>`__, `ensemblonly <#ensemblonly>`__, `exists <#exists>`__, `missing <#missing>`__, `filter <#filter>`__, `post_filter <#post-filter>`__, `always_list <#always-list>`__, `allow_null <#allow-null>`__, `jmespath <#jmespath>`__, `jmespath_exclude_empty <#jmespath-exclude-empty>`__, `format <#format>`__, `rawquery <#rawquery>`__ and `raw <#raw>`__. "**from**", "**sort**" and the filters apply to the hits of each query term.

Example code
------------

Unlike GET requests, you can easily test them from browser, make a POST request is often done via a
piece of code. Here is a sample python snippet::

    import requests
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    params = 'q=1017,1018&scopes=entrezgene&fields=name,symbol,taxid,entrezgene'
    res = requests.post('http://mygene.info/v3/query', data=params, headers=headers)

You can also send the parameters as JSON, which returns the same result::

    import requests
    params = {'q': ['1017', '1018'], 'scopes': 'entrezgene', 'fields': 'name,symbol,taxid,entrezgene'}
    res = requests.post('http://mygene.info/v3/query', json=params)


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
.. Note:: if no "fields" parameter is specified, the default fields "symbol,name,taxid,entrezgene" are returned. Pass "fields=all" to get all available fields.

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

A query term also comes back as "**notfound**" when "**from**" skips all of its hits, or "**jmespath_exclude_empty**" leaves them all out.

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

.. _with_total_example:

With "**with_total**", the hits come in an object that also tells you whether some query terms have more hits than "**size**"::

    params = 'q=cdk2,1017&scopes=symbol,entrezgene&fields=symbol,taxid&size=2&with_total=true'
    res = requests.post('http://mygene.info/v3/query', data=params, headers=headers)

.. code-block:: json

    {
      "max_total": 1041,
      "hits": [
        {
          "query": "cdk2",
          "_id": "1017",
          "_score": 148.79999,
          "symbol": "CDK2",
          "taxid": 9606
        },
        {
          "query": "cdk2",
          "_id": "12566",
          "_score": 124.799995,
          "symbol": "Cdk2",
          "taxid": 10090
        },
        {
          "query": "1017",
          "_id": "1017",
          "_score": 27.462214,
          "symbol": "CDK2",
          "taxid": 9606
        }
      ],
      "msg": "1 query terms return > 2 hits, using from=2 to retrieve the remaining hits"
    }


Compound queries
----------------

A query term can also be a list of values, to match each value against its own scopes, e.g., a gene symbol in one field and a species in another. Pass "**scopes**" as a list with one entry per value, in the same order; an entry can itself be a list of fields. A gene is a hit only if every value matches. This request looks up CDK2 in a different species for each query term::

    import requests
    params = {
        'q': [['CDK2', '9606'], ['Cdk2', '10090'], ['cdk2', '7955']],
        'scopes': ['symbol', 'taxid'],
        'fields': 'symbol,taxid',
    }
    res = requests.post('http://mygene.info/v3/query', json=params)

.. code-block:: json

    [
      {
        "query": ["CDK2", "9606"],
        "_id": "1017",
        "_score": 150.34999,
        "symbol": "CDK2",
        "taxid": 9606
      },
      {
        "query": ["Cdk2", "10090"],
        "_id": "12566",
        "_score": 126.1,
        "symbol": "Cdk2",
        "taxid": 10090
      },
      {
        "query": ["cdk2", "7955"],
        "_id": "406715",
        "_score": 106.700005,
        "symbol": "cdk2",
        "taxid": 7955
      }
    ]

With a form-encoded body, pass "**q**" as JSON, e.g., ``q=[["CDK2","9606"],["Cdk2","10090"]]&scopes=symbol,taxid``. To give a value a list of fields, e.g., ``"scopes": [["entrezgene", "symbol"], "taxid"]``, send the parameters as JSON.







.. raw:: html

    <div id="spacer" style="height:300px"></div>
