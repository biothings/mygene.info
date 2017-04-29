Third-party packages
======================

This page lists third-party packages/modules built upon `MyGene.info <http://mygene.info>`_ services.

MyGene python module
----------------------
"`mygene <https://pypi.python.org/pypi/mygene>`_" is an easy-to-use Python wrapper to access `MyGene.info <http://mygene.info>`_ services.

You can install it easily using either `pip <http://www.pip-installer.org>`_ or `easy_install <https://pypi.python.org/pypi/setuptools>`_::

    pip install mygene               #this is preferred

or::

    easy_install mygene

This is a brief example:

.. code-block :: python

    In [1]: import mygene

    In [2]: mg = mygene.MyGeneInfo()

    In [3]: mg.getgene(1017)
    Out[3]:
    {'_id': '1017',
     'entrezgene': 1017,
     'name': 'cyclin-dependent kinase 2',
     'symbol': 'CDK2',
     'taxid': 9606}

    In [4]:  mg.query('cdk2', size=2)
    Out[4]:
    {'hits': [{'_id': '1017',
       '_score': 373.24667,
       'entrezgene': 1017,
       'name': 'cyclin-dependent kinase 2',
       'symbol': 'CDK2',
       'taxid': 9606},
      {'_id': '12566',
       '_score': 353.90176,
       'entrezgene': 12566,
       'name': 'cyclin-dependent kinase 2',
       'symbol': 'Cdk2',
       'taxid': 10090}],
     'max_score': 373.24667,
     'took': 10,
     'total': 28}

See https://pypi.python.org/pypi/mygene for more details.


MyGene R package
-------------------
An R wrapper for the MyGene.info API is available in Bioconductor since v3.0.  To install::

    source("https://bioconductor.org/biocLite.R")
    biocLite("mygene")

To view documentation for your installation, enter R and type::

    browseVignettes("mygene")

For more information, visit the `Bioconductor mygene page <https://www.bioconductor.org/packages/release/bioc/html/mygene.html>`_.



MyGene autocomplete widget
--------------------------
This autocomplete widget for gene query (built upon `JQueryUI's autocomplete widget <http://api.jqueryui.com/autocomplete/>`_) provides suggestions while you type a gene symbol or name into the field. You can easily embed it into your web application. It also provides many customization options for your different use-cases.

See https://bitbucket.org/sulab/mygene.autocomplete/overview for more details.

You can also play with this `jsFiddle <http://jsfiddle.net/frm3X/>`_ example:

.. raw:: html

    <script async src="//jsfiddle.net/frm3X/embed/"></script>



Another MyGene Python wrapper
------------------------------
This is yet another Python wrapper of MyGene.info services created by `Brian Schrader <http://brianschrader.com/about/>`__. It's hosted at https://github.com/Sonictherocketman/mygene-api.

It's available from `PyPI <https://pypi.python.org/pypi/mygene-api>`__ as well::

    pip install mygene-api
    

Some basic examples:

*  Find a given gene with the id: CDK2.

.. code-block :: python

    """ Use the query API to find a gene with 
    the given symbol.
    """
    from mygene.gene import Gene

    results = Gene.find_by(q='CDK2')
    for r in result:
        print r._id, r.name

    >>> 1017 cyclin-dependent kinase 2
    12566 cyclin-dependent kinase 2
    362817 cyclin dependent kinase 2
    52004 CDK2-associated protein 2
    ...

  
*  Given an known gene, get it's begin and end coordinates. 

.. code-block :: python

    """ Use the annotation API to find the full 
    details of a given gene.
    """
    from mygene.gene import gene

    gene = Gene.get('1017')
    print gene._id, gene.genomic_pos_hg19['start'], gene.genomic_pos_hg19['end']

    >>> 1017 56360553 56366568
   

*  This library also supports the metadata API.

.. code-block :: python
   
    from mygene.metadata import Metadata

    metadata = Metadata.get_metadata()
    print metadata.stats['total_genes']

    >>> 12611464


.. raw:: html

    <div id="spacer" style="height:300px"></div>
