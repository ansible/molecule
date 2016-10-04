********
Molecule
********

.. image:: https://badge.fury.io/py/molecule.svg
   :target: https://badge.fury.io/py/molecule
   :alt: PyPI Package

.. image:: https://readthedocs.org/projects/molecule/badge/?version=latest
   :target: https://molecule.readthedocs.org/en/latest/
   :alt: Documentation Status

Molecule is designed to aid in the development and testing of
`Ansible`_ roles including support for multiple instances,
operating system distributions, virtualization providers and test frameworks.

It leverages `Vagrant`_, `Docker`_, and `OpenStack`_ to manage virtual
machines/containers, with support for multiple Vagrant providers (currently
`VirtualBox`_, `Parallels`_, `VMware Fusion`_, and `Libvirt`_).  Molecule
supports `Serverspec`_, `Testinfra`_, or `Goss`_ (beta) to run tests.  Molecule
uses an `Ansible`_ `playbook`_ (``playbook.yml``), to execute the `role`_ and
its tests.

.. _`Test Kitchen`: http://kitchen.ci
.. _`playbook`: https://docs.ansible.com/ansible/playbooks.html
.. _`role`: http://docs.ansible.com/ansible/playbooks_roles.html

Ansible Support
===============

* 1.9.6 - Limited (`Docker`_ driver not-supported by `Ansible`_)
* 2.0.2.0 - Supported
* 2.1.1.0 - Supported

Dependencies
============

Molecule relies on several outside packages and programs to function.

* `Ansible`_

Verifier
--------

* `Goss`_
* `Serverspec`_
* `Testinfra`_ (default)

Driver
------

* `Docker`_
* `Openstack`_
* `Vagrant`_ (default)

Provider
--------

* `Libvirt`_
* `VirtualBox`_ (default)
* `VMware Fusion`_
* `Parallels`_

.. _`Ansible`: https://docs.ansible.com
.. _`Docker`: https://www.docker.com
.. _`Goss`: https://github.com/aelsabbahy/goss
.. _`Libvirt`: http://libvirt.org
.. _`OpenStack`: https://www.openstack.org
.. _`Parallels`: http://www.parallels.com
.. _`Serverspec`: http://serverspec.org
.. _`Testinfra`: http://testinfra.readthedocs.org
.. _`Vagrant`: http://docs.vagrantup.com/v2
.. _`VirtualBox`: https://www.virtualbox.org
.. _`VMware Fusion`: http://www.vmware.com/products/fusion.html

Quick Start
===========

.. important::

  `Ansible`_ and the driver's python package require installation.

Install molecule using pip:

.. code-block:: bash

  $ pip install ansible
  $ pip install docker-py
  $ pip install molecule

Create a new role with the docker driver:

.. code-block:: bash

  $ molecule init --role foo --driver docker
  --> Initializing role foo...
  Successfully initialized new role in ./foo


Or add molecule to an existing role:

.. code-block:: bash

  $ cd foo
  $ molecule init --driver docker
  --> Initializing molecule in current directory...
  Successfully initialized new role in /private/tmp

Update the role with needed functionality and tests.  Now test it:

.. code-block:: bash

  $ cd foo
  $ molecule test
  --> Destroying instances ...
  --> Checking playbooks syntax ...

  playbook: playbook.yml
  --> Creating instances ...
  --> Creating Ansible compatible image of ubuntu:latest ...
  --> Creating Ansible compatible image of ubuntu:latest ...
  Creating container foo-01 with base image ubuntu:latest ...
  Container created.
  Creating container foo-02 with base image ubuntu:latest ...
  Container created.
  --> Starting Ansible Run ...

  PLAY [all] *********************************************************************

  TASK [setup] *******************************************************************
  ok: [foo-01]
  ok: [foo-02]

  PLAY RECAP *********************************************************************
  foo-01                     : ok=1    changed=0    unreachable=0    failed=0
  foo-02                     : ok=1    changed=0    unreachable=0    failed=0

  --> Idempotence test in progress (can take a few minutes)...
  --> Starting Ansible Run ...
  Idempotence test passed.
  --> Executing ansible-lint.
  --> Executing flake8 on \*.py files found in tests/.
  --> Executing testinfra tests found in tests/.
  ============================= test session starts ==============================
  platform darwin -- Python 2.7.11, pytest-2.9.2, py-1.4.31, pluggy-0.3.1
  rootdir: /private/tmp/foo/tests, inifile:
  plugins: xdist-1.14, testinfra-1.4.1
  collected 2 itemss

  tests/test_default.py ..

  =========================== 2 passed in 1.52 seconds ===========================
  --> Destroying instances ...
  Stopping container foo-01 ...
  Removed container foo-01.
  Stopping container foo-02 ...
  Removed container foo-02.

Documentation
=============

http://molecule.readthedocs.org/en/latest/

License
=======

MIT

The logo is licensed under the `Creative Commons NoDerivatives 4.0 License`_.  If you have some other use in mind, contact us.

.. _`Creative Commons NoDerivatives 4.0 License`: https://creativecommons.org/licenses/by-nd/4.0/
