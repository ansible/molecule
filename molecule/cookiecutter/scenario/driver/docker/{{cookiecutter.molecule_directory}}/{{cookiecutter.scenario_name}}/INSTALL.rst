*******
Install
*******

This set of playbooks have specific dependencies on Ansible due to the modules
being used.

Requirements
============

* Ansible 2.2
* docker-py

Install OS dependencies on CentOS 6/7

.. code-block:: bash

  $ yum install -y epel-release
  $ yum install gcc python-devel openssl-devel libffi-devel

Install OS dependencies on Ubuntu 16.x

.. code-block:: bash

  $ apt-get update
  $ apt-get install gcc python-pip python-vagrant libssl-dev libffi-dev

Install using pip:

.. code-block:: bash

  $ pip install ansible
  $ pip install docker-py
  $ pip install molecule
