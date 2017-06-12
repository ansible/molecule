*******
Install
*******

This set of playbooks have specific dependencies on Ansible due to the modules
being used.

Requirements
============

* Ansible 2.2
* LXC
* lxc-python2

Install OS dependencies on CentOS 7

.. code-block:: bash

  $ sudo yum install -y epel-release
  $ sudo yum install -y gcc python-pip python-devel openssl-devel lxc lxc-devel lxc-extra
  # If installing Molecule from source.
  $ sudo yum install libffi-devel git

Install OS dependencies on Ubuntu 16.x

.. code-block:: bash

  $ sudo apt-get update
  $ sudo apt-get install -y python-pip libssl-dev lxc lxc-dev
  # If installing Molecule from source.
  $ sudo apt-get install -y libffi-dev git

Install OS dependencies on Mac OS

.. code-block:: bash

  Not supported.

Install using pip:

.. code-block:: bash

  $ sudo pip install ansible
  $ sudo pip install lxc-python2
  $ sudo pip install molecule --pre

.. important::

  The Ansible LXC modules do not support unprivileged containers.  To properly
  use this driver, one must prefix each Molecule command with `sudo`.
