Migration from v1 API
=====================

Migrating from v1 API to v2 API should be very trival. Here is a summary for the changes:

Gene query service
^^^^^^^^^^^^^^^^^^^

URL change
"""""""""""

Starting from v2 API, we added "/v2" as the prefix for service urls:

:v1: http://mygene.info/v1/query or http://mygene.info/query

:v2: http://mygene.info/v2/query


Returned Objects
""""""""""""""""""
There are some small changes in returned gene objects as summarized here:

* "rows"       ➡ "hits"
* "total_rows" ➡ "total"
* "id" ➡ "_id"  ("_" prefix indicates interval fields)
* "score" ➡ "_score"
* removed in v2: "homologene", "skip", "limit", "etag"
* added in v2: "entrezgene" (Entrez gene id), "max_score", "took"


You can also see the differences in the following examples:

.. raw:: html

    <div class="v1_box">


**v1:**  http://mygene.info/v1/query?q=symbol:cdk2&limit=1

.. code-block:: json
    :linenos:
    :emphasize-lines: 2,4,15,18

    {
        "rows": [
            {
                "id": "1017",

                "symbol": "CDK2",
                "taxid": 9606,
                "name": "cyclin-dependent kinase 2",
                "homologene": {
                    "genes": [[9606,1017],[10090,12566],
                              [10116,362817],[7227,42453],
                              [7955,406715],[3702,824036]],
                    "id": 74409
                },
                "score": 72.55062866210938
            }
        ],
        "total_rows": 6,


        "skip": 0,
        "etag": "4f1b7983a4",
        "limit": 1
    }

.. raw:: html

    </div>
    <div class="v2_box">


**v2:**   http://mygene.info/v2/query?q=symbol:cdk2&size=1

.. code-block:: json
    :linenos:
    :emphasize-lines: 2,4,15,18

    {
        "hits": [
            {
                "_id": "1017",
                "entrezgene": 1017,
                "symbol": "CDK2",
                "taxid": 9606,
                "name": "cyclin-dependent kinase 2",






                "_score": 89.32175
            }
        ],
        "total": 3,
        "max_score": 89.32175,
        "took": 4



    }

.. raw:: html

    </div>





Gene annotation service
^^^^^^^^^^^^^^^^^^^^^^^

URL change
"""""""""""

Starting from v2 API, we added "/v2" as the prefix for service urls:

:v1: http://mygene.info/v1/gene or http://mygene.info/gene

:v2: http://mygene.info/v2/gene


Returned Objects
""""""""""""""""""
The returned objects are essentially back-compatible in v2, except that gene object in v2 contains even more fields as we expand underlying annotation data.




.. raw:: html

    <div id="spacer" style="height:300px"></div>


