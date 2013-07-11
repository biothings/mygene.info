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




MyGene autocomplete widget
--------------------------
This autocomplete widget for gene query (built upon `JQueryUI's autocomplete widget <http://api.jqueryui.com/autocomplete/>`_) provides suggestions while you type a gene symbol or name into the field. You can easily embed it into your web application. It also provides many customization options for your different use-cases.

See https://bitbucket.org/sulab/mygene.autocomplete/overview for more details.

You can also play with it with this `jsFiddle <http://jsfiddle.net/frm3X/>`_ example:

.. raw:: html

    <iframe width="100%" height="400" src="http://jsfiddle.net/frm3X/embedded/js,resources,html,result/presentation/" allowfullscreen="allowfullscreen" frameborder="0"></iframe>


.. raw:: html

    <div id="spacer" style="height:300px"></div>
