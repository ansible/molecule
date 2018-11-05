.. _installation:

************
Installation
************

This document assumes the developer has a basic understanding of python
packaging, and how to install and manage python on the system executing
Molecule.

Requirements
============

Depending on the driver chosen, you may need to install additional OS packages.
See ``INSTALL.rst``, which is created when initializing a new scenario.

* :std:doc:`Ansible <ansible:index>` >= 2.4
* Python 2.7
* Python >= 3.6 with Ansible >= 2.4

CentOS 7
--------

.. code-block:: bash

    $ sudo yum install -y epel-release
    $ sudo yum install -y gcc python-pip python-devel openssl-devel libselinux-python

Ubuntu 16.x
-----------

.. code-block:: bash

    $ sudo apt-get update
    $ sudo apt-get install -y python-pip libssl-dev

Pip
===

:std:doc:`pip <pip:usage>` is the only supported installation method.

Requirements
------------

Depending on the driver chosen, you may need to install additional python
packages.  See the driver's documentation or `INSTALL.rst`, which is created
when initializing a new scenario.

Install
-------

Install Molecule:

.. code-block:: bash

    $ sudo pip install molecule

Source
======

Due to the rapid pace of development on this tool, you might want to install it
in "`development mode`_" so that new updates can be obtained by simply doing a
``git pull`` in the repository's directory.

Requirements
------------

CentOS 7
^^^^^^^^

.. code-block:: bash

    $ sudo yum install -y libffi-devel git

Ubuntu 16.x
^^^^^^^^^^^

.. code-block:: bash

    $ sudo apt-get install -y libffi-dev git

Install
-------

.. code-block:: bash

    $ cd /path/to/molecule/checkout
    $ pip install -U -e .

.. _`development mode`: https://setuptools.readthedocs.io/en/latest/setuptools.html#development-mode
