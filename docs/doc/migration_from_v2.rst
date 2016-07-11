Migration from v2 API
=====================

Migrating from v2 API to v3 API is easy. Here's a summary of the changes.
You may also want to read our `blog <http://mygene.info/mygene-info-v3-is-out>`_
for complementary information.


URL change
^^^^^^^^^^^

You will need to access v3 API using "**/v3**" prefix for service urls:

Gene query service endpoint
"""""""""""""""""""""""""""

:v2: http://mygene.info/v2/query
:v3: http://mygene.info/v3/query

Gene annotation service endpoint
"""""""""""""""""""""""""""""""""

:v2: http://mygene.info/v2/gene
:v3: http://mygene.info/v3/gene


Returned Objects
^^^^^^^^^^^^^^^^^

There are several small changes in the returned data structure, as summarized here:



Accession number with version
""""""""""""""""""""""""""""""

"**refseq**" and "**accession**" fields now contain accession number including version.
Data can be search with and without version. Version is available for "`genomic`",
"`rna`" and "`protein`" accession number keys.

.. note:: "*genomic*" field is returned but is not searchable



.. raw:: html

    <div class="v1_box">


**v2:**  http://mygene.info/v2/query?q=NM_052827&fields=refseq.rna

.. code-block:: json
    :linenos:
    :emphasize-lines: 7-10

    {
      "hits": [
      {
        "_id": "1017",
        "refseq": {
          "rna": [
            "NM_001290230",
            "NM_001798",
            "NM_052827",
            "XM_011537732"
          ]
        }
      }
    ],
      "max_score": 0.51962745,
      "took": 3,
      "total": 1

    }

.. raw:: html

    </div>
    <div class="v2_box">


**v3:**   http://mygene.info/v3/query?q=NM_052827&fields=refseq.rna

.. code-block:: json
    :linenos:
    :emphasize-lines: 8-11

    {
      "hits": [
        {
          "_id": "1017",
          "_score": 10.052136,
          "refseq": {
            "rna": [
              "NM_001290230.1",
              "NM_001798.4",
              "NM_052827.3",
              "XM_011537732.1"
            ]
          }
        }
      ],
      "total": 1,
      "took": 14,
      "max_score": 10.052136
    }

.. raw:: html

    </div>


"translation" field for RNA-protein mapping
"""""""""""""""""""""""""""""""""""""""""""""

For "**ensembl**", "**refseq**" and "**accession**" fields, a new sub-field name "*translation*" is
now available. It gives the association between RNA and its protein product. v2 does not
have this information in returned objects.


**v3:**   http://mygene.info/v3/query?q=NM_052827&fields=refseq.translation,refseq.rna,refseq.protein

.. code-block:: json
    :linenos:
    :emphasize-lines: 21-38

    {
      "max_score": 10.052136,
      "total": 1,
      "hits": [
        {
          "_id": "1017",
          "_score": 10.052136,
          "refseq": {
            "protein": [
              "NP_001277159.1",
              "NP_001789.2",
              "NP_439892.2",
              "XP_011536034.1"
            ],
            "rna": [
              "NM_001290230.1",
              "NM_001798.4",
              "NM_052827.3",
              "XM_011537732.1"
            ],
            "translation": [
              {
                "protein": "XP_011536034.1",
                "rna": "XM_011537732.1"
              },
              {
                "protein": "NP_001789.2",
                "rna": "NM_001798.4"
              },
              {
                "protein": "NP_439892.2",
                "rna": "NM_052827.3"
              },
              {
                "protein": "NP_001277159.1",
                "rna": "NM_001290230.1"
              }
            ]
          }
        }
      ],
      "took": 4
    }

"exons" data structure modification
""""""""""""""""""""""""""""""""""""

.. warning:: Backward-incompatible, data structure changed

"**exons**" field has two major modifications. It now contains a list of dictionary instead
of a dictionary indexed by the accession number. This accession number is found within
the dictionary under the key "*transcript*". Finally, inner "*exons*" key has been
rename to "*position*".



.. raw:: html

    <div class="v1_box">

**v2:**  http://mygene.info/v2/gene/1698?fields=exons

.. code-block:: json
    :linenos:
    :emphasize-lines: 3,4,10

    {
      "_id": "259236",
      "exons": {
        "NM_147196": {
          "cdsstart": 46701487,
          "cdsend": 46709688,
          "txstart": 46701332,
          "txend": 46710923,
          "chr": "3",
          "exons": [
            [
              46701332,
              46701580
            ],
            [
              46705789,
              46705907
            ],
            [
              46709125,
              46709275
            ],
            [
              46709578,
              46710923
            ]
          ],
          "strand": 1
        }
      }


    }

.. raw:: html

    </div>
    <div class="v2_box">

**v3:**   http://mygene.info/v3/gene/1698?fields=exons

.. code-block:: json
    :linenos:
    :emphasize-lines: 4,9,28

    {
      "_id": "259236",
      "_score": 21.732534,
      "exons": [
        {
          "cdsend": 46709688,
          "cdsstart": 46701487,
          "chr": "3",
          "position": [
            [
              46701332,
              46701580
            ],
            [
              46705789,
              46705907
            ],
            [
              46709125,
              46709275
            ],
            [
              46709578,
              46710923
            ]
          ],
          "strand": 1,
          "transcript": "NM_147196",
          "txend": 46710923,
          "txstart": 46701332
        }
      ]
    }

.. raw:: html

    </div>





"dotfield" notation default changed
""""""""""""""""""""""""""""""""""""

.. warning:: May be backward-incompatible, default data structure changed (but can be restored with "*dotfield*" paramater setting)

By default, "**dotfield**" notation is now disabled for gene annotation endpoint in v3 (/gene). It's enabled by default in v2.
You will need to explicitely pass "**dotfield=1**" to your queries to have the same behavior as v2.

.. Note:: "**dotfield**" notation is disabled by default for gene query endpoint (/gene) in both v2 and v2



.. raw:: html

    <div class="v1_box">

**v2:**  http://mygene.info/v2/gene/1017?fields=refseq.rna

.. code-block:: json
    :linenos:
    :emphasize-lines: 4

    {

      "_id": "1017",
      "refseq.rna": [
        "NM_001290230",
        "NM_001798",
        "NM_052827",
        "XM_011537732"
      ]


    }


.. raw:: html

    </div>
    <div class="v2_box">


**v3:**   http://mygene.info/v3/gene/1017?fields=refseq.rna

.. code-block:: json
    :linenos:
    :emphasize-lines: 4,5

    {
      "_id": "1017",
      "_score": 21.731894,
      "refseq": {
        "rna": [
          "NM_001290230.1",
          "NM_001798.4",
          "NM_052827.3",
          "XM_011537732.1"
        ]
      }
    }

.. raw:: html

    </div>


Querying "reporter" data source
""""""""""""""""""""""""""""""""

"reporter" data now has to be queried explicitelty, prefixing the query term by "reporter:"

**v3:**    http://mygene.info/v3/query?q=reporter:2845421&fields=reporter
