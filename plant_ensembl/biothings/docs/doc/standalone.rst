##############################
BioThings Standalone instances
##############################

This step-by-step guide shows how to use Biothings standalone instances. Standalones instances
are based on Docker containers and provide and fully pre-configured, ready-to-use Biothings API
that can easily be maintained and kept up-to-date. The idea is, for any user, to be able to run
her own APIs locally, fulfulling differents needs:

* keep all APIs requests private and local to your own server
* enriching existing and publicly available data found on our APIs with some private data
* run API on your own architecture to perform heavy queries that would sometimes be throttled out from
  online services

***********
Quick Links
***********

If you already know how to run a BioThings standalone instance, you can download the latest
avaiable Docker images from the following tables.

.. note:: Images don't contain data but are ready to download and maintain data up-to-date
          running simple commands through the hub.

.. _`contact us`: biothings@googlegroups.com

|mygenelogo|
^^^^^^^^^^^^
.. |mygenelogo| image:: ../_static/mygene-text.png
   :width: 200px
   :alt: MyGene.info

Production and old data require at least 30GiB disk space.

+----------------+------------+------------+
| Production     | Demo       | Old        |
+================+============+============+
| `Contact us`__ | Download__ | Download__ |
+----------------+------------+------------+

.. __: mailto:help@mygene.info
.. __: http://biothings-containers.s3-website-us-west-2.amazonaws.com/demo_mygene/demo_mygene.docker
.. __: http://biothings-containers.s3-website-us-west-2.amazonaws.com/old_mygene/old_mygene.docker

|myvariantlogo|
^^^^^^^^^^^^^^^
.. |myvariantlogo| image:: ../_static/myvariant-text.png
   :width: 200px
   :alt: MyVariant.info

Production and old data require at least 2TiB disk space.

+----------------+------------+------------+
| Production     | Demo       | Old        |
+================+============+============+
| `Contact us`__ | Download__ | Download__ |
+----------------+------------+------------+

.. __: mailto:help@myvariant.info
.. __: http://biothings-containers.s3-website-us-west-2.amazonaws.com/demo_myvariant/demo_myvariant.docker
.. __: http://biothings-containers.s3-website-us-west-2.amazonaws.com/old_myvariant/old_myvariant.docker

|mychemlogo|
^^^^^^^^^^^^
.. |mychemlogo| image:: ../_static/mychem-text.png
   :width: 200px
   :alt: MyChem.info

Production and old data require at least 150Gib disk space.

+----------------+------------+------------+
| Production     | Demo       | Old        |
+================+============+============+
| `Contact us`__ | Download__ | Soon !     |
+----------------+------------+------------+

.. __: mailto:help@mygene.info
.. __: http://biothings-containers.s3-website-us-west-2.amazonaws.com/demo_mychem/demo_mychem.docker

*************
Prerequisites
*************

Using standalone instances requires to have a Docker server up and running, some basic knowledge
about commands to run and use containers. Images have been tested on Docker >=17. Using AWS cloud,
you can use our public AMI **biothings_demo_docker** (``ami-44865e3c`` in Oregon region) with Docker pre-configured
and ready for standalone demo instances deployment. We recommend using instance type with at least
8GiB RAM, such as ``t2.large``. AMI comes with an extra 30GiB EBS volume, which should be enough to
deploy any demo instances.

Alternately, you can install your own Docker server (on recent Ubuntu systems, ``sudo apt-get install docker.io``
is usually enough). You may need to point Docker images directory to a specific hard drive to get enough space,
using ``-g`` option:

.. code:: bash

  # /mnt/docker points to a hard drive with enough disk space
  sudo echo 'DOCKER_OPTS="-g /mnt/docker"' >> /etc/default/docker
  # restart to make this change active
  sudo service docker restart

Demo instances use very little disk space, as only a small subset of data is available.
For instance, myvariant demo only requires ~10GiB to run with demo data up-to-date, including the whole Linux
system and all other dependencies. Demo instances provide a quick and easy way to setup a running APIs,
without having to deal with some advanced system configurations.

For deployment with production or old data, you may need a large amount of disk space.
Refer to the `Quick Links`_ section for more information. Bigger instance types will also be
required, and even a full cluster architecture deployment. We'll soon provide guidelines and
deployment scripts for this purpose.


*****************
What you'll learn
*****************

Through this guide, you'll learn:

* how to obtain a Docker image to run your favorite API
* how to run that image inside a Docker container and how to access the web API
* how to connect to the *hub*, a service running inside to container used to interact with the API systems
* how to use that hub, using specific commands, in order to perform update and keep data up-to-date

**********************************
Data found in standalone instances
**********************************

All BioThings APIs (mygene.info, myvariant.info, ...) provide data release in different flavors:

* **Production data**, the actual data found on live APIs we, the BioThings team at `SuLab <http://sulab.org>`_, are running and keeping up-to-date on a regular basis.
  Please contact us if you're interested in obtaining this type of data.
* **Demo data**, a small subset of production data, publicly available
* **Old production data**, an at least one year old production dataset (full), publicly available

The following guide applies to demo data only, though the process would be very similar for other types of data flavors.


*********************************************
Downloading and running a standalone instance
*********************************************

Standalone instances are available as Docker images. For the purpose of this guide, we'll setup an instance running mygene API,
containing demo data. Links to standalone demo Docker images, can be found in `Quick links`_ at the beginning of this guide.
Use one of these links, or use this `direct link <http://biothings-containers.s3-website-us-west-2.amazonaws.com/demo_mygene/demo_mygene.docker>`_
to mygene's demo instance, and download the Docker image file, using your favorite browser or ``wget``:

.. code:: bash

  $ wget http://biothings-containers.s3-website-us-west-2.amazonaws.com/demo_mygene/demo_mygene.docker

You must have a running Docker server in order to use that image. Typing ``docker ps`` should return all running containers, or
at least an empty list as in the following example. Depending on the systems and configuration, you may have to add ``sudo``
in front of this command to access Docker server.

.. code:: bash

  $ docker ps
    CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS      NAMES

Once downloaded, the image can be loaded into the server:

.. code:: bash

  $ docker image load < demo_mygene.docker
  $ docker image list
  REPOSITORY                                                          TAG                 IMAGE ID            CREATED             SIZE
  demo_mygene                                                         latest              15d6395e780c        6 weeks ago         1.78GB

Image is now loaded, size is ~1.78GiB, it contains no data (yet). An docker container can now be instantiated from that image, to
create a BioThings standalone instance, ready to be used.

A standalone instance is a pre-configured system containing several parts. BioThings hub is the system used to interact
with BioThings backend and perform operations such as downloading data and create/update ElasticSearch indices. Those
indices are used by the actual BioThings web API system to serve data to end-users. The hub can be accessed through a standard
SSH connection or through REST API calls. In this guide, we'll use the SSH server.

A BioThings instance expose several services on different ports:

* **80**: BioThings web API port
* **7022**: BioThings hub SSH port
* **7080**: BioThings hub REST API port
* **9200**: ElasticSearch port

We will map and expose those ports to the host server using option ``-p`` so we can access BioThings services without
having to enter the container (eg. hub ssh port here will accessible using port 19022).

.. code:: bash

  $ docker run --name demo_mygene -p 19080:80 -p 19200:9200 -p 19022:7022 -p 19090:7080 -d demo_mygene

.. note:: Instance will store ElasticSearch data in `/var/lib/elasticsearch/` directory, and downloaded data and logs
          in ``/data/`` directory. Those two locations could require extra disk space, if needed Docker option ``-v``
          can be used to mount a directory from the host, inside the container. Please refer to Docker documnentation.

.. _services:

Let's enter the container to check everything is running fine. Services may take a while, up to 1 min, before fully started.
If some services are missing, the troubleshooting section may help.

.. code:: bash

  $ docker exec -ti demo_mygene /bin/bash

  root@a6a6812e2969:/tmp# netstat -tnlp
  Active Internet connections (only servers)
  Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
  tcp        0      0 0.0.0.0:7080            0.0.0.0:*               LISTEN      -
  tcp        0      0 0.0.0.0:7022            0.0.0.0:*               LISTEN      -
  tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      25/nginx
  tcp        0      0 127.0.0.1:8881          0.0.0.0:*               LISTEN      -
  tcp        0      0 127.0.0.1:8882          0.0.0.0:*               LISTEN      -
  tcp        0      0 127.0.0.1:8883          0.0.0.0:*               LISTEN      -
  tcp        0      0 127.0.0.1:8884          0.0.0.0:*               LISTEN      -
  tcp        0      0 127.0.0.1:8885          0.0.0.0:*               LISTEN      -
  tcp        0      0 127.0.0.1:8886          0.0.0.0:*               LISTEN      -
  tcp        0      0 127.0.0.1:8887          0.0.0.0:*               LISTEN      -
  tcp        0      0 127.0.0.1:8888          0.0.0.0:*               LISTEN      -
  tcp6       0      0 :::7080                 :::*                    LISTEN      -
  tcp6       0      0 :::7022                 :::*                    LISTEN      -
  tcp6       0      0 :::9200                 :::*                    LISTEN      -
  tcp6       0      0 :::9300                 :::*                    LISTEN      -

We can see the different BioThings services' ports: 7080, 7022 and 7080. All 888x ports
correspond to Tornado instances running behing Nginx port 80. They shouldn't be accessed directly.
Ports 9200 and 9300 are ElasticSearch standard ports (9200 one can be used to perform queries directly on ES, if needed)

At this point, the standalone instance is up and running. No data has been downloaded yet, let's see how to
populate the BioThings API using the hub.

*********************************
Updating data using Biothings hub
*********************************

If the standalone instance has been freshly started, there's no data to be queried by the API. If we make a API call,
such as fetching metadata, we'll get an error:

.. code:: bash

  # from Docker host
  $ curl -v http://localhost:19080/metadata
    *   Trying 127.0.0.1...
    * Connected to localhost (127.0.0.1) port 19080 (#0)
    > GET /metadata HTTP/1.1
    > Host: localhost:19080
    > User-Agent: curl/7.47.0
    > Accept: */*
    >
    < HTTP/1.1 500 Internal Server Error
    < Date: Tue, 28 Nov 2017 18:19:23 GMT
    < Content-Type: text/html; charset=UTF-8
    < Content-Length: 93
    < Connection: keep-alive
    < Server: TornadoServer/4.5.2
    <
    * Connection #0 to host localhost left intact

This 500 error reflects a missing index (ElasticSearch index, the backend used by BioThings web API). We can have a look at
existing indices in ElasticSearch:

.. code:: bash

  # from Docker host
  $ curl http://localhost:19200/_cat/indices
  yellow open hubdb 5 1 0 0 795b 795b

There's only one index, ``hubdb``, which is an internal index used by the hub. No index containing actual biological data...

BioThings hub is a service running inside the instance, it can be accessed through a SSH connection, or using REST API calls.
For the purpose of the guide, we'll use SSH. Let's connect to the hub (type ``yes`` to accept the key on first connection):

.. code:: bash

  # from Docker host
  $ ssh guest@localhost -p 19022
  The authenticity of host '[localhost]:19022 ([127.0.0.1]:19022)' can't be established.
  RSA key fingerprint is SHA256:j63IEgXc3yJqgv0F4wa35aGliH5YQux84xxABew5AS0.
  Are you sure you want to continue connecting (yes/no)? yes
  Warning: Permanently added '[localhost]:19022' (RSA) to the list of known hosts.

  Welcome to Auto-hub, guest!
  hub>

We're now connected to the hub, inside a python shell where the application is actually running. Let's see what commands are available:

.. warning:: the hub console, though accessed through SSH, is **not** a Linux shell (such as `bash`), it's a python interpreter shell.

.. code:: bash

  hub> help()

  Available commands:

          versions
          check
          info
          download
          apply
          step_update
          update
          help

  Type: 'help(command)' for more

* ``versions()`` will display all available data build versions we can download to populate the API
* ``check()`` will return whether a more recent version is available online
* ``info()`` will display current local API version, and information about the latest available online
* ``download()`` will download the data compatible with current local version (but without populating the ElasticSearch index)
* ``apply()`` will use local data previously downloaded to populate the index
* ``step_update()`` will bring data release to the next one (one step in versions), compatible with current local version
* ``update()`` will bring data to the latest available online (using a combination of ``download`` and ``apply`` calls)

.. note:: ``update()`` is the fastest, easiest and preferred way to update the API. ``download``, ``apply``, ``step_update`` are available
          when it's necessary to bring the API data to a specific version (not the latest one), are considered more advanced,
          and won't be covered in this guide.

.. note:: Because the hub console is actually a python interpreter, we call the commands using parenthesis, just like functions
          or methods. We can also pass arguments when necessary, just like standard python (remember: it **is** python...)

.. note:: After each command is typed, we need to press "enter" to get either its status (still running) or the result

Let's explore some more.

.. code:: bash

  hub> info()
  [2] RUN {0.0s} info()
  hub>
  [2] OK  info(): finished
  >>> Current local version: 'None'
  >>> Release note for remote version 'latest':
  Build version: '20171126'
  =========================
  Previous build version: '20171119'
  Generated on: 2017-11-26 at 03:11:51

  +---------------------------+---------------+-------------+-----------------+---------------+
  | Updated datasource        | prev. release | new release | prev. # of docs | new # of docs |
  +---------------------------+---------------+-------------+-----------------+---------------+
  | entrez.entrez_gene        |    20171118   |   20171125  |          10,003 |        10,003 |
  | entrez.entrez_refseq      |    20171118   |   20171125  |          10,003 |        10,003 |
  | entrez.entrez_unigene     |    20171118   |   20171125  |          10,003 |        10,003 |
  | entrez.entrez_go          |    20171118   |   20171125  |          10,003 |        10,003 |
  | entrez.entrez_genomic_pos |    20171118   |   20171125  |          10,003 |        10,003 |
  | entrez.entrez_retired     |    20171118   |   20171125  |          10,003 |        10,003 |
  | entrez.entrez_accession   |    20171118   |   20171125  |          10,003 |        10,003 |
  | generif                   |    20171118   |   20171125  |          10,003 |        10,003 |
  | uniprot                   |    20171025   |   20171122  |          10,003 |        10,003 |
  +---------------------------+---------------+-------------+-----------------+---------------+

  Overall, 9,917 documents in this release
  0 document(s) added, 0 document(s) deleted, 130 document(s) updated

We can see here we don't have any local data release (``Current local version: 'None'``), whereas the latest online (at that time) is from
November 26th 2017. We can also see the release note with the different changes involved in the release (whether it's a new version, or the number
of documents that changed).

.. code:: bash

  hub> versions()
  [1] RUN {0.0s} versions()
  hub>
  [1] OK  versions(): finished
  version=20171003             date=2017-10-05T09:47:59.413191 type=full
  version=20171009             date=2017-10-09T14:47:10.800140 type=full
  version=20171009.20171015    date=2017-10-19T11:44:47.961731 type=incremental
  version=20171015.20171022    date=2017-10-25T13:33:16.154788 type=incremental
  version=20171022.20171029    date=2017-11-14T10:34:39.445168 type=incremental
  version=20171029.20171105    date=2017-11-06T10:55:08.829598 type=incremental
  version=20171105.20171112    date=2017-11-14T10:35:04.832871 type=incremental
  version=20171112.20171119    date=2017-11-20T07:44:47.399302 type=incremental
  version=20171119.20171126    date=2017-11-27T10:38:03.593699 type=incremental

Data comes in two distinct types:

* **full**: this is a full data release, corresponding to an ElasticSearch snapshot, containing all the data
* **incremental** : this is a differential/incremental release, produced by computing the differences between two consecutives versions.
  The diff data is then used to patch an existing, compatible data release to bring it to the next version.

So, in order to obtain the latest version, the hub will first find a compatible version. Since it's currently empty (no data), it will
use the first **full** release from 20171009, and then apply **incremental** updates sequentially (``20171009.20171015``, then ``20171015.20171022``,
then ``20171022.20171029``, etc... up to ``20171119.20171126``).

Let's update the API:

.. code:: bash

  hub> update()
  [3] RUN {0.0s} update()
  hub>
  [3] RUN {1.3s} update()
  hub>
  [3] RUN {2.07s} update()

After a while, the API is up-to-date, we can run command ``info()`` again (it also can be used to track update progress):

.. code:: bash

  hub> info()
  [4] RUN {0.0s} info()
  hub>
  [4] OK  info(): finished
  >>> Current local version: '20171126'
  >>> Release note for remote version 'latest':
  Build version: '20171126'
  =========================
  Previous build version: '20171119'
  Generated on: 2017-11-26 at 03:11:51

  +---------------------------+---------------+-------------+-----------------+---------------+
  | Updated datasource        | prev. release | new release | prev. # of docs | new # of docs |
  +---------------------------+---------------+-------------+-----------------+---------------+
  | entrez.entrez_gene        |    20171118   |   20171125  |          10,003 |        10,003 |
  | entrez.entrez_refseq      |    20171118   |   20171125  |          10,003 |        10,003 |
  | entrez.entrez_unigene     |    20171118   |   20171125  |          10,003 |        10,003 |
  | entrez.entrez_go          |    20171118   |   20171125  |          10,003 |        10,003 |
  | entrez.entrez_genomic_pos |    20171118   |   20171125  |          10,003 |        10,003 |
  | entrez.entrez_retired     |    20171118   |   20171125  |          10,003 |        10,003 |
  | entrez.entrez_accession   |    20171118   |   20171125  |          10,003 |        10,003 |
  | generif                   |    20171118   |   20171125  |          10,003 |        10,003 |
  | uniprot                   |    20171025   |   20171122  |          10,003 |        10,003 |
  +---------------------------+---------------+-------------+-----------------+---------------+

  Overall, 9,917 documents in this release
  0 document(s) added, 0 document(s) deleted, 130 document(s) updated


Local version is ``20171126``, remote is ``20171126``, we're up-to-date. We can also use ``check()``:

.. code:: bash

  hub> check()
  [5] RUN {0.0s} check()
  hub> 
  [5] OK  check(): finished 
  Nothing to dump

``Nothing to dump`` means there's no available remote version that can be downloaded. It would otherwise return a version number, meaning
we would be able to update the API again using command ``update()``.

Press Control-D to exit from the hub console.

Querying ElasticSearch, we can see a new index, named ``biothings_current``, has been created and populated:

.. code:: bash

  $ curl http://localhost:19200/_cat/indices
  green  open biothings_current 1 0 14903 0 10.3mb 10.3mb
  yellow open hubdb             5 1     2 0 11.8kb 11.8kb

We now have a populated API we can query:

.. code:: bash

  # from Docker host
  # get metadata (note the build_version field)
  $ curl http://localhost:19080/metadata
  {
    "app_revision": "672d55f2deab4c7c0e9b7249d22ccca58340a884",
    "available_fields": "http://mygene.info/metadata/fields",
    "build_date": "2017-11-26T02:58:49.156184",
    "build_version": "20171126",
    "genome_assembly": {
      "rat": "rn4",
      "nematode": "ce10",
      "fruitfly": "dm3",
      "pig": "susScr2",
      "mouse": "mm10",
      "zebrafish": "zv9",
      "frog": "xenTro3",
      "human": "hg38"
    },

  # annotation endpoint
  $ curl http://localhost:19080/v3/gene/1017?fields=alias,ec
  {
    "_id": "1017",
    "_score": 9.268311,
    "alias": [
      "CDKN2",
      "p33(CDK2)"
    ],
    "ec": "2.7.11.22",
    "name": "cyclin dependent kinase 2"
  }

  # query endpoint
  $ curl http://localhost:19080/v3/query?q=cdk2
  {
    "max_score": 310.69254,
    "took": 37,
    "total": 10,
    "hits": [
      {
        "_id": "1017",
        "_score": 310.69254,
        "entrezgene": 1017,
        "name": "cyclin dependent kinase 2",
        "symbol": "CDK2",
        "taxid": 9606
      },
      {
        "_id": "12566",
        "_score": 260.58084,
        "entrezgene": 12566,
        "name": "cyclin-dependent kinase 2",
        "symbol": "Cdk2",
        "taxid": 10090
      },
  ...




***********************************
BioThings API with multiple indices
***********************************

Some APIs use more than one ElasticSearch index to run. For instance, myvariant.info uses one index for hg19 assembly, and one index
for hg38 assembly. With such APIs, the available commands contain a suffix showing which index (thus, which data release) they relate to.
Here's the output of ``help()`` from myvariant's standalone instance:

.. code:: bash

  hub> help()

  Available commands:

  	versions_hg19
  	check_hg19
  	info_hg19
  	download_hg19
  	apply_hg19
  	step_update_hg19
  	update_hg19
  	versions_hg38
  	check_hg38
  	info_hg38
  	download_hg38
  	apply_hg38
  	step_update_hg38
  	update_hg38
  	help


For instance, ``update()`` command is now available as ``update_hg19()`` and ``update_hg38()`` depending on the assemlby.


***************
Troubleshooting
***************

We test and make sure, as much as we can, that standalone images are up-to-date and hub is properly running for each
data release. But things can still go wrong...

First make sure all services are running. Enter the container and type ``netstat -tnlp``, you should see
services running on ports (see usual running `services`_). If services running on ports 7080 or 7022 aren't running,
it means the hub has not started. If you just started the instance, wait a little more as services may take a while before
they're fully started and ready.

If after ~1 min, you still don't see the hub running, log to user ``biothings`` and check the starting sequence.

.. note:: Hub is running in a tmux session, under user ``biothings``

.. code:: bash

  # sudo su - biothings
  $ tmux a # recall tmux session

  python -m biothings.bin.autohub
  (pyenv) biothings@a6a6812e2969:~/mygene.info/src$ python -m biothings.bin.autohub
  INFO:root:Hub DB backend: {'module': 'biothings.utils.es', 'host': 'localhost:9200'}
  INFO:root:Hub database: hubdb
  DEBUG:asyncio:Using selector: EpollSelector
  start

You should see something looking like this above. If not, you should see the actual error, and depending on the error, you may be able to
fix it (not enough disk space, etc...). The hub can be started again using ``python -m biothings.bin.autohub`` from within the application
directory (in our case, ``/home/biothings/mygene.info/src/``)

.. note:: Press Control-B then D to dettach the tmux session and let the hub running in background.

Logs are available in ``/data/mygene.info/logs/``. You can have a look at:

* ``dump_*.log`` files for logs about data download
* ``upload_*.log`` files for logs about index update in general (full/incremental)
* ``sync_*.log`` files for logs about incremental update only
* and ``hub_*.log`` files for general logs about the hub process

Finally, you can report issues and request for help, by joining Biothings Google Groups (https://groups.google.com/forum/#!forum/biothings)

