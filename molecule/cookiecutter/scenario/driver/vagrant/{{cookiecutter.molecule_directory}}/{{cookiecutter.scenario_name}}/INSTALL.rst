*******
Install
*******

This set of playbooks have specific dependencies on Ansible due to the modules
being used.

Requirements
============

* Ansible 2.2
* Vagrant
* Virtualbox, Parallels, VMware Fusion, VMware Workstation or VMware Desktop
* python-vagrant

Install OS dependencies on CentOS 7

.. code-block:: bash

  $ sudo yum install -y epel-release
  $ sudo yum install -y gcc python-pip openssl-devel
  # If installing Molecule from source.
  $ sudo yum install libffi-devel

Install OS dependencies on Ubuntu 16.x

.. code-block:: bash

  $ sudo apt-get update
  $ sudo apt-get install -y python-pip libssl-dev vagrant virtualbox
  # If installing Molecule from source.
  $ sudo apt-get install -y libffi-dev

Install OS dependencies on Mac OS

.. code-block:: bash

  $ brew install python

Install using pip:

.. code-block:: bash

  $ pip install ansible
  $ pip install python-vagrant
  $ pip install molecule
