#############
Hub component
#############

The purpose of the BioThings hub component is to allow you to easily automate the parsing and uploading of your data to an Elasticsearch backend.

.. py:module:: biothings

******
dumper
******

BaseDumper
==========

.. autoclass:: biothings.hub.dataload.dumper.BaseDumper
    :members:

FTPDumper
---------

.. autoclass:: biothings.hub.dataload.dumper.FTPDumper
    :members:

HTTPDumper
----------

.. autoclass:: biothings.hub.dataload.dumper.HTTPDumper
    :members:

GoogleDriveDumper
+++++++++++++++++

.. autoclass:: biothings.hub.dataload.dumper.GoogleDriveDumper
    :members:

WgetDumper
----------

.. autoclass:: biothings.hub.dataload.dumper.WgetDumper
    :members:

DummyDumper
-----------

.. autoclass:: biothings.hub.dataload.dumper.DummyDumper
    :members:

ManualDumper
-----------

.. autoclass:: biothings.hub.dataload.dumper.ManualDumper
    :members:

********
uploader
********

BaseSourceUploader
==================

.. autoclass:: biothings.hub.dataload.uploader.BaseSourceUploader
    :members:

NoBatchIgnoreDuplicatedSourceUploader
-------------------------------------

.. autoclass:: biothings.hub.dataload.uploader.NoBatchIgnoreDuplicatedSourceUploader
    :members:

IgnoreDuplicatedSourceUploader
------------------------------

.. autoclass:: biothings.hub.dataload.uploader.IgnoreDuplicatedSourceUploader
    :members:

MergerSourceUploader
--------------------

.. autoclass:: biothings.hub.dataload.uploader.MergerSourceUploader
    :members:

DummySourceUploader
-------------------

.. autoclass:: biothings.hub.dataload.uploader.DummySourceUploader
    :members:

ParallelizedSourceUploader
--------------------------

.. autoclass:: biothings.hub.dataload.uploader.ParallelizedSourceUploader
    :members:

NoDataSourceUploader
--------------------

.. autoclass:: biothings.hub.dataload.uploader.NoDataSourceUploader
    :members:

*******
builder
*******

DataBuilder
===========

.. autoclass:: biothings.hub.databuild.builder.DataBuilder
    :members:

*******
indexer
*******

Indexer
=======

.. autoclass:: biothings.hub.dataindex.indexer.Indexer
    :members:

******
differ
******

BaseDiffer
==========

.. autoclass:: biothings.hub.databuild.differ.BaseDiffer
    :members:

JsonDiffer
----------

.. autoclass:: biothings.hub.databuild.differ.JsonDiffer
    :members:

SelfContainedJsonDiffer
+++++++++++++++++++++++

.. autoclass:: biothings.hub.databuild.differ.SelfContainedJsonDiffer
    :members:

DiffReportRendererBase
======================

.. autoclass:: biothings.hub.databuild.differ.DiffReportRendererBase
    :members:   

DiffReportTxt
-------------

.. autoclass:: biothings.hub.databuild.differ.DiffReportTxt
    :members:

******
syncer
******

BaseSyncer
==========

.. autoclass:: biothings.hub.databuild.syncer.BaseSyncer
    :members:

MongoJsonDiffSyncer
-------------------

.. autoclass:: biothings.hub.databuild.syncer.MongoJsonDiffSyncer
    :members:

MongoJsonDiffSelfContainedSyncer
--------------------------------

.. autoclass:: biothings.hub.databuild.syncer.MongoJsonDiffSelfContainedSyncer
    :members:

ESJsonDiffSyncer
----------------

.. autoclass:: biothings.hub.databuild.syncer.ESJsonDiffSyncer
    :members:

ESJsonDiffSelfContainedSyncer
-----------------------------

.. autoclass:: biothings.hub.databuild.syncer.ESJsonDiffSelfContainedSyncer
    :members:
