.. _installation:

************
Installation
************

System Requirements
-------------------

CentOS 7
^^^^^^^^

.. code-block:: bash

    $ sudo yum install -y epel-release
    $ sudo yum install -y gcc python-pip python-devel openssl-devel libselinux-python

Ubuntu 16.x
^^^^^^^^^^^

.. code-block:: bash

    $ sudo apt-get update
    $ sudo apt-get install -y python-pip libssl-dev

Python Requirements
-------------------

* :std:doc:`Ansible <ansible:index>` >= 2.4
* Python 2.7
* Python >= 3.6 with Ansible >= 2.4

Install Molecule using :std:doc:`pip <pip:usage>`:

.. code-block:: bash

    $ pip install --user molecule

Installing the Molecule package also installs the main script ``molecule``,
usually on your ``$PATH``. Users should know that molecule can also be called
as a python module, using ``python -m molecule ...``. This alternative method
has some benefits:

* allows to explicitly control which python interpreter is used by molecule
* allows molecule installation at the user level without even needing to have
  the script in ``$PATH``.

Driver Requirements
-------------------

Depending on the driver chosen, you may need to install additional system
packages.  See ``INSTALL.rst``, which is created when initializing a new
scenario.
