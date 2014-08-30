Autocomplete widget for gene query
===================================

When you build a web application to have users to query for their favorite genes, the autocomplete widget is very useful, as it provides suggestions while users start to type into the field.

.. Note:: The autocomplete widget below is a simple demo application. You may also want to have a look at `this more sophisticated autocomplete widget <packages.html#mygene-autocomplete-widget>`_, which comes with a lot more customization options.


Try it live first
^^^^^^^^^^^^^^^^^^^^

.. raw:: html

    <div style=' text-align:center'>
     <label for="gene_query">Enter a gene here (e.g., CDK2): </label>
     <input style="width:250px" class="mygene_query_target">
     <script src="http://mygene.info/widget/autocomplete/js/mygene_query_min.js" type="text/javascript"></script>
    </div>

About this widget
^^^^^^^^^^^^^^^^^^^^

This autocomplete widget for gene query provides suggestions while you type a gene symbol or name into the field. Here the gene suggestions are displayed as "<Symbol>:<Name>", automatically triggered when at least two characters are entered into the field.

At the backend, this widget is powered by `the gene query web service </doc/query_service.html>`_ from `MyGene.info <http://mygene.info>`_. By default, the gene suggestions display human genes only.


Use it in your website
^^^^^^^^^^^^^^^^^^^^^^^

To use this widget in your own website is very easy, just following these three steps:

1. Copy/paste this line into your html file::

    <script src="http://mygene.info/widget/autocomplete/js/mygene_query_min.js" type="text/javascript"></script>


.. Hint:: if you prefer an un-minified javascript file, using "mygene_query.js" instead.

2. Add "**mygene_query_target**" class to your target input element::

    <input id="gene_query" style="width:250px" class="mygene_query_target">

so that we know which input field to enable autocomplete.

3. Define your own callback function, which is triggered after user selects a gene. For example::

    <script type="text/javascript">
        mygene_query_select_callback = function(event, ui){
                alert( ui.item ?
                    "Selected: " + ui.item.label + '('+ui.item.entrezgene+')':
                    "Nothing selected, input was " + this.value);
        };
    </script>

As shown in above example, you can access the gene object as **ui.item**::

    ui.item._id       gene id
    ui.item.value    gene symbol
    ui.item.label    the label displayed in autocomplete dropdown list

.. Note:: if you don't define your own callback function (like the minimal HTML page below), the default behavior is to display an alert msg with the gene selected. To change this default behavior, you must overwrite with your own callback function (keep the same name as "**mygene_query_select_callback**").

A minimal HTML page with autocomplete enabled looks just like this (`See it in action here <http://mygene.info/widget/autocomplete/demo_minimal.html>`_):

.. code-block:: html

    <html>
    <body>
        <label for="gene_query">Enter a gene here: </label>
        <input style="width:250px" class="mygene_query_target">
        <script src="http://mygene.info/widget/autocomplete/js/mygene_query_min.js" type="text/javascript"></script>
    </body>
    </html>

Have fun! And send us feedback at <help@mygene.info>.


