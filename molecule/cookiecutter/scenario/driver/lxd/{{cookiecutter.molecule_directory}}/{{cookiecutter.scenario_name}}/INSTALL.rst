*******
Install
*******

This set of playbooks have specific dependencies on Ansible due to the modules
being used.

Requirements
============

* Ansible 2.2
* LXD

Install OS dependencies on CentOS 7

.. code-block:: bash

  Not supported.

Install OS dependencies on Ubuntu 16.x

.. code-block:: bash

  $ sudo apt-get update
  $ sudo apt-get install -y python-pip python-devel libssl-dev lxd
  # If installing Molecule from source.
  $ sudo apt-get install -y libffi-dev git

Install OS dependencies on Mac OS

.. code-block:: bash

  Not supported.

Install using pip:

.. code-block:: bash

  $ sudo pip install ansible
  $ sudo pip install molecule
