*******
Install
*******

This set of playbooks have specific dependencies on Ansible due to the modules
being used.

Requirements
============

* Ansible 2.2
* Docker Engine
* docker-py

Install OS dependencies on CentOS 7

.. code-block:: bash

  $ sudo yum install -y epel-release
  $ sudo yum install -y gcc python-pip openssl-devel
  # If installing Molecule from source.
  $ sudo yum install libffi-devel

Install OS dependencies on Ubuntu 16.x

.. code-block:: bash

  $ sudo apt-get update
  $ sudo apt-get install -y python-pip libssl-dev docker-engine
  # If installing Molecule from source.
  $ sudo apt-get install -y libffi-dev

Install OS dependencies on Mac OS

.. code-block:: bash

  $ brew install python

Install using pip:

.. code-block:: bash

  $ pip install ansible
  $ pip install docker-py
  $ pip install molecule
