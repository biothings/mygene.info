***************************************
Docker Development Environment Tutorial 
***************************************

The following tutorial demonostrates how to setup a development environment
for a sample application, biothings.interactions, using docker.  All of the
required images are provided by the Su lab's docker registry server and 
application configuration is provided by versioned configuration files.


Prerequisites
^^^^^^^^^^^^^

Install docker on your local development system or on a server
having at least 2 GB of RAM.  The community edition of docker is fine 
for the purposes of this tutorial.

`Docker Installation <https://docs.docker.com/engine/installation/>`

Evaluation Environment
======================

The evaluation version of biothings.interactions downloads and starts the following containers:

* biothings.data - an nginx server containing randomized data 
* mongodb - the mongodb server running version 3.2 
* elasticsearch - the ElasticSearch server running version 5.6.4 
* biothings.interactions - the server built by the Dockerfile in this directory

We need to generate ssh keys that will be used by the biothings.api hub.  You need some form of the
program `ssh-keygen`, I use git-bash on Windows.

.. code-block:: bash
    ssh-keygen -f ssh_host_key

Download the biothings.interactions evaluation docker compose file.

`Evaluation Docker Compose File <https://gist.github.com/greg-k-taylor/b86a0148620ed63b47c0f745e862b446>`

Download and run all required containers using `docker-compose`.

.. code-block:: bash
    docker-compose -f docker-compose-evaluation.yml up 

You may now connect to the hub or mongo db using the following commands:

.. code-block:: bash
    # Connect to the HUB
    docker exec -it biothings.interactions bash 
    ssh guest@localhost -p 8022
    # Connect to Mongo DB
    docker exec -it mongodb mongo

Note:  There is a reason why connecting to the hub is a 2 step process.  Using this configuration,
all network activity between services is done on a docker network named biothings.  For security
reasons, there is no way to access these containers except through docker.

Development Environment
=======================

The development environment is very similar to the evaluation version except
that application code and configuration files are dropped into directly and
replaced the existing application version in the container.  This allows the
developer to make simple changes to the application and restart the hub
service, reflecting those changes, with two commands.

Download the biothings.docker repository:
.. code-block:: bash
    git clone https://github.com/greg-k-taylor/biothings.docker.git
    cd biothings.docker/biothings.interactions

Generate ssh keys just as you did for the evaluation version.

.. code-block:: bash
    ssh-keygen -f ssh_host_key

Download biothings.interactions application source.

.. code-block:: bash
    git clone https://github.com/biothings/biothings.interactions.git

Run the docker environment using `docker-compose`, mounting the local version 
of biothings.interactions in place of the existing one in the image.

.. code-block:: bash
    docker-compose -f docker-compose-development.yml up 

Now may now connect to the development stack as described above in the evaluation section!
If you make changes to the application inside of `biothings.interactions`, restart the
containers with

.. code-block:: bash
    docker-compose -f docker-compose-development.yml down
    docker-compose -f docker-compose-development.yml up 

