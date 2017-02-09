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

Install OS dependencies on CentOS 6/7

.. code-block:: bash

  TODO

Install OS dependencies on Ubuntu 16.x

.. code-block:: bash

  $ sudo apt-get update
  $ sudo apt-get install -y python-pip libssl-dev libffi-dev lxc lxc-dev

Install using pip:

.. code-block:: bash

  $ pip install ansible
  $ pip install lxc-python2
  $ pip install molecule

.. important::

  The Ansible LXC modules do not support unprivileged containers.  To properly
  use this driver, one must prefix each Molecule command with `sudo`.
