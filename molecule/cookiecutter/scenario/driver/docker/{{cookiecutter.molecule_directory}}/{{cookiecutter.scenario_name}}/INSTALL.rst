*******
Docker driver installation guide
*******

Requirements
============

* General molecule dependencies (see https://molecule.readthedocs.io/en/latest/installation.html)
* Docker Engine
* docker-py
* docker

Install
=======

Ansible < 2.6

.. code-block:: bash

    $ sudo pip install docker-py

Ansible >= 2.6

.. code-block:: bash

    $ sudo pip install docker
