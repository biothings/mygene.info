.. Response status

Server response
***************

The MyGene.info server returns a variety of query responses, and response status codes.  They are listed here.

.. note:: These examples show query responses using the python `requests <http://docs.python-requests.org/en/master/>`_ package.

Status code *200*
-----------------

A **200** status code indicates a successful query, and is accompanied by the query response payload.

.. code-block :: python

    In [1]: import requests

    In [2]: r = requests.get('http://mygene.info/v3/query?q=_exists_:entrezgene')

    In [3]: r.status_code
    Out[3]: 200

    In [4]: data = r.json()

    In [5]: data.keys()
    Out[5]: dict_keys(['total', 'max_score', 'took', 'hits'])


Status code *400*
-----------------

A **400** status code indicates an improperly formed query, and is accompanied by a response payload describing the source of the error.

.. code-block :: python

    In [6]: r = requests.get('http://mygene.info/v3/query?q=_exists_:entrezgene&size=u')

    In [7]: r.status_code
    Out[7]: 400

    In [8]: data = r.json()

    In [9]: data
    Out[9]: 
    {'error': "Expected 'size' parameter to have integer type.  Couldn't convert 'u' to integer",
     'success': False}

Status code *404*
-----------------

A **404** status code indicates either an unrecognized URL, as in (*/query* is misspelled */quer* resulting in an unrecognized URL):

.. code-block :: python

    In [10]: r = requests.get('http://mygene.info/v3/quer?q=_exists_:entrezgene')

    In [11]: r.status_code
    Out[11]: 404

or, for the **/gene** endpoint, a **404** status code could be from querying for a nonexistent gene ID, as in:

.. code-block :: python

    In [12]: r = requests.get('http://mygene.info/v3/gene/0')

    In [13]: r.status_code
    Out[13]: 404

    In [14]: data = r.json()

    In [15]: data
    Out[15]: 
    {'error': "Gene ID '0' not found",
     'success': False}

Status code *5xx*
-----------------

Any **5xx** status codes are the result of uncaught query errors.  Ideally, these should never occur.  We routinely check our logs for these types of errors and add code to catch them, but if you see any status **5xx** responses, please submit a bug report to `help@mygene.info <mailto:help@mygene.info>`_.
