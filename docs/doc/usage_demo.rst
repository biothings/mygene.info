Usage and Demo
***************

This page provides some usage examples and demo applications.

Call from web applications
==================================================

You can call MyGene.info services from either server-side or client-side (via AJAX). The sample code can be found at `"demo" section <#demo-applications>`_.

Calling services from server-side
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All common programing languages provide functions for making http requests and JSON parsing. For Python, you can using build-in `httplib <http://docs.python.org/library/httplib.html>`_ and `json <http://docs.python.org/library/json.html>`__ modules (v2.6 up), or third-party `httplib2 <http://code.google.com/p/httplib2/>`_ and `simplejson <http://pypi.python.org/pypi/simplejson>`_ modules. For Perl, `LWP::Simple <http://search.cpan.org/~gaas/libwww-perl-5.837/lib/LWP/Simple.pm>`_ and `JSON <http://search.cpan.org/~makamaka/JSON-2.50/lib/JSON.pm>`_ modules should work nicely.


Making AJAX calls from client-side
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
When making an AJAX call from a web application, it is restricted by `"same-origin" security policy <http://en.wikipedia.org/wiki/Same_origin_policy>`_, but there are several standard ways to get it around.

Making your own server-side proxy
"""""""""""""""""""""""""""""""""

    To overcome "same-origin" restriction, you can create proxy at your server-side to our services. And then call your proxied services from your web application.

    Setup proxy in popular server-side applications, like `Apache <http://www.ghidinelli.com/2008/12/27/how-to-bypass-cross-domain-restrictions-when-developing-ajax-applications>`_, `Nginx <http://wiki.nginx.org/NginxHttpProxyModule>`_ and `PHP <http://developer.yahoo.com/javascript/howto-proxy.html>`_, are straightforward.

Making JSONP call
"""""""""""""""""

    Because our core services are just called as simple GET http requests (though we support POST requests for batch queries too), you can bypass "same-origin" restriction by making JSONP call as well. To read more about JSONP, see `1 <http://en.wikipedia.org/wiki/JSONP#JSONP>`_, `2 <http://remysharp.com/2007/10/08/what-is-jsonp/>`_, or just Google about it. All our services accept an optional "**callback**" parameter, so that you can pass your callback function to make a JSONP call.

    All popular javascript libraries have the support for making JSONP calls, like in `JQuery <http://api.jquery.com/jQuery.getJSON/>`_, `ExtJS <http://docs.sencha.com/extjs/4.2.1/#!/api/Ext.data.proxy.JsonP>`_, `MooTools <http://mootools.net/docs/more/Request/Request.JSONP>`_

Cross-origin http request through CORS
""""""""""""""""""""""""""""""""""""""

    Cross-Origin Resource Sharing (CORS) specification is a `W3C draft specification <http://www.w3.org/TR/cors/>`_ defining client-side cross-origin requests. It's actually supported by all major browsers by now (Internet Explorer 8+, Firefox 3.5+, Safari 4+, and Chrome. See more on `browser support <http://caniuse.com/cors>`_), but not many people are aware of it. Unlike JSONP, which is limited to GET requests only, you can make cross-domain POST requests as well. Our services supports CORS requests on both GET and POST requests. You can find more information and use case `here <http://blog.timothyfisher.com/?p=285>`__ and `here <http://hacks.mozilla.org/2009/07/cross-site-xmlhttprequest-with-cors/>`__.

    JQuery's native ajax call supports CORS since v1.5.


.. _demo:

Demo Applications
=================

In this demo, we want to create a web site to display expression charts from a microarray dataset (Affymetrix MOE430v2 chip). The expression data are indexed by porobeset ids, but we need to allow users to query for any mouse genes using any commonly-used identifiers, and then display expression charts for any selected gene.

We implemented this demo in four ways:


Example 1: using CGI
^^^^^^^^^^^^^^^^^^^^

 * `Download sample code here <http://mygene.info/_static/demo/mygene_info_demo_cgi.py>`__.

 * It's a simple python CGI script. To run it, you just need to drop it to your favorite web server's cgi-bin folder (make sure your python, v2.6 up, is in the path).

 * `See it in action here <http://sulab.scripps.edu/cgi-bin/mygene_info_demo.cgi>`__.

Example 2: using tornado
^^^^^^^^^^^^^^^^^^^^^^^^^

    * `Download sample code here <http://mygene.info/_static/demo/mygene_info_demo_tornado.py>`__.
    * This single python script can be used to run a standalone website. Just run: ``python mygene_info_demo_tornado.py``.You then have your website up at ``http://localhost:8000``.

    Besides python (v2.6 up), you also need `tornado <http://www.tornadoweb.org>`_ to run this code. You can either install it by your own (``pip install tornado``), or download `this zip file <http://mygene.info/_static/demo/mygene_info_demo_tornado.zip>`_, which includes tornado in it.

    * `See it in action here </demo/mygene_info_demo_tornado>`__.

Example 3: using JSONP
^^^^^^^^^^^^^^^^^^^^^^^^

 * `Download sample code here <http://mygene.info/_static/demo/mygene_info_demo_jsonp.zip>`__.

 * The zip file contains one html file and one javascript file. There is no server-side code at all. To run it, just unzip it and open the html file in any browser. All remote service calls are done at client side (via browsers). Put the files into any web server serving static files will allow you to publish to the world.

 * `See it in action here <http://mygene.info/_static/demo/mygene_info_demo_jsonp.html>`__.

Example 4: using CORS
^^^^^^^^^^^^^^^^^^^^^^^

 * `Download sample code here <http://mygene.info/_static/demo/mygene_info_demo_cors.zip>`__.

 * The zip file contains one html file and one javascript file. There is no server-side code at all. To run it, just unzip it and open the html file in any browser. All remote service calls are done at client side (via browsers). Put the files into any web server serving static files will allow you to publish to the world.

 * This demo is almost the same as the one using JSONP, except that the actual AJAX call to MyGene.info server is made via CORS.


 * `See it in action here <http://mygene.info/_static/demo/mygene_info_demo_cors.html>`__.


.. include :: autocomplete.rst


.. raw:: html

    <div id="spacer" style="height:300px"></div>
