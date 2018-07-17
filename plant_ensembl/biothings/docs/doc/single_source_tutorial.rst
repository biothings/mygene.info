***********************************************
Single Data Source, No Source Updating Tutorial
***********************************************

The following tutorial shows a minimal use case for the BioThings SDK: creating a
high-performance, high-concurrency API from a single flat-file.  The BioThings SDK
is broadly divided into two components, the hub and the web.  The hub component is a
collection of tools to automate the downloading of source data files, the merging
of different sources, and the updating of the Elasticsearch index.  The web component
is a Tornado-based API app that subsequently serves data from this Elasticsearch index.

Prerequisites
^^^^^^^^^^^^^

Before starting, there are a few requirements that need to be installed and configured.

Python
======

The BioThings SDK requires `Python version 3.4 or higher <https://www.python.org/>`_ for full functionality.
We recommend installing all python dependencies into a `virtualenv <https://virtualenv.pypa.io/en/stable/>`_.

BioThings SDK
=============

Either install from source, like:

.. code-block:: bash
    
    git clone https://github.com/biothings/biothings.api.git
    cd biothings.api
    python setup.py install

or use pip, like:

.. code-block:: bash

    pip install biothings

or directly from our repository, like:

.. code-block:: bash

    pip install git+https://github.com/biothings/biothings.api.git#egg=biothings

Elasticsearch
=============

BioThings APIs currently serve data from an Elasticsearch index, so Elasticsearch is a requirement.
Install Elasticsearch 2.4 either `directly <https://www.elastic.co/guide/en/elasticsearch/reference/2.4/_installation.html>`_,
or as a `docker container <https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html>`_.

Configure Elasticsearch
+++++++++++++++++++++++

To configure Elasticsearch, execute the following commands as su:

.. code-block:: bash

    echo 'http.enabled: True' >> /etc/elasticsearch/elasticsearch.yml
    echo 'network.host: "0.0.0.0"' >> /etc/elasticsearch/elasticsearch.yml

.. note:: This guide was created using Ubuntu 16.04, the exact location of elasticsearch.yml may vary in other platforms.

PharmGKB Gene
^^^^^^^^^^^^^

Once all prerequisites have been installed and Elasticsearch is running, the data loading step can begin.
Consider the following script, which defines a "load_data" function that parses
the `PharmGKB gene flat file <https://api.pharmgkb.org/v1/download/file/data/genes.zip>`_ and then iterates through it, storing the results in an Elasticsearch index using biothings.utils.es.ESIndexer.

.. code-block:: python

    In [1]: import re

    In [2]: from biothings.utils.es import ESIndexer

    In [3]: def load_data(f):
       ...:     for (i, line) in enumerate(f):
       ...:         line = line.strip('\n')
       ...:         if i == 0:  # get the column header names in the first row
       ...:             header_dict = dict([(p, re.sub(r'\s', '_', h.lower())) for (p, h) in enumerate(line.split('\t'))])
       ...:         else:
       ...:             _r = {}
       ...:             for (pos, val) in enumerate(line.split('\t')):
       ...:                 if val:
       ...:                     _r[header_dict[pos]] = val if '","' not in val else val.strip('"').split('","')
       ...:             yield _r
       ...:

    In [4]: indexer = ESIndexer(index='pharmgkb_gene_current', doc_type='pharmgkb_gene', es_host='localhost:9200')

    In [5]: indexer.create_index(mapping={'pharmgkb_gene':{'dynamic': True}})

    In [6]: with open('genes.tsv', 'r') as gene_file:
       ...:     indexer.index_bulk(load_data(gene_file))

Generate BioThings API 
^^^^^^^^^^^^^^^^^^^^^^

Now that we have an Elasticsearch index with our indexed gene data in it, we can create and start
an API.  Change to a directory you want to store the front-end code, and type:

.. code-block:: bash

    biothings-admin.py pharmgkb_gene . -o src_package=pharmgkb_gene

Now you can start your API by typing:

.. code-block:: bash

    cd pharmgkb_gene/src
    pip install -r ../requirements_web.txt
    python web/index.py --debug --port=8001

Your API is live.  To use it, you can query it with a curl (or your local browser).  For example,
if you wanted to find the PharmGKB accession for an NCBI gene (or gene list) you have, you could do a query
like:

.. code-block:: bash

    curl "http://localhost:8001/v1/query?q=ncbi_gene_id:1017&fields=pharmgkb_accession_id"
    {
      "max_score": 8.178926,
      "took": 9,
      "total": 1,
      "hits": [
        {
          "_id": "AVydiHIJYMgArMwkfE8R",
          "_score": 8.178926,
          "pharmgkb_accession_id": "PA101"
        }
      ]
    }

Or, to find all PharmGKB genes that have a CDK* symbol, you can do this query:

.. code-block:: bash

    curl "http://localhost:8001/v1/query?q=symbol:CDK*&fields=pharmgkb_accession_id,symbol"
    {
      "max_score": 1.0,
      "took": 11,
      "total": 50,
      "hits": [
        {
          "_id": "AVydiHIJYMgArMwkfE8F",
          "_score": 1.0,
          "pharmgkb_accession_id": "PA99",
          "symbol": "CDK1"
        },
        {
          "_id": "AVydiHIJYMgArMwkfE8H",
          "_score": 1.0,
          "pharmgkb_accession_id": "PA26263",
          "symbol": "CDK11A"
        },
        {
          "_id": "AVydiHIJYMgArMwkfE8M",
          "_score": 1.0,
          "pharmgkb_accession_id": "PA165696414",
          "symbol": "CDK15"
        },
        {
          "_id": "AVydiHIJYMgArMwkfE8R",
          "_score": 1.0,
          "pharmgkb_accession_id": "PA101",
          "symbol": "CDK2"
        },
        {
          "_id": "AVydiHIJYMgArMwkfE8n",
          "_score": 1.0,
          "pharmgkb_accession_id": "PA26317",
          "symbol": "CDKL1"
        },
        {
          "_id": "AVydiHIJYMgArMwkfE8N",
          "_score": 1.0,
          "pharmgkb_accession_id": "PA33095",
          "symbol": "CDK16"
        },
        {
          "_id": "AVydiHIJYMgArMwkfE8e",
          "_score": 1.0,
          "pharmgkb_accession_id": "PA38632",
          "symbol": "CDK5RAP2"
        },
        {
          "_id": "AVydiHIJYMgArMwkfE8h",
          "_score": 1.0,
          "pharmgkb_accession_id": "PA26314",
          "symbol": "CDK7"
        },
        {
          "_id": "AVydiHIJYMgArMwkfE8m",
          "_score": 1.0,
          "pharmgkb_accession_id": "PA134871999",
          "symbol": "CDKAL1"
        },
        {
          "_id": "AVydiHIJYMgArMwkfE8v",
          "_score": 1.0,
          "pharmgkb_accession_id": "PA106",
          "symbol": "CDKN2A"
        }
      ]
    }
