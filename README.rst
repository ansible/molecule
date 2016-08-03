.. image:: https://cloud.githubusercontent.com/assets/9895/11258895/12a1bb40-8e12-11e5-9adf-9a7aea1ddda9.png
   :alt: Molecule
   :width: 500
   :height: 132
   :align: center

Molecule
========

.. image:: https://badge.fury.io/py/molecule.svg
   :target: https://badge.fury.io/py/molecule
   :alt: PyPI Package

.. image:: https://readthedocs.org/projects/molecule/badge/?version=latest
   :target: https://molecule.readthedocs.org/en/latest/
   :alt: Documentation Status

.. image:: https://travis-ci.org/rgreinho/molecule.svg?branch=master
   :target: https://travis-ci.org/rgreinho/molecule
   :alt: Build Status

.. image:: https://requires.io/github/rgreinho/molecule/requirements.svg?branch=master
   :target: https://requires.io/github/rgreinho/molecule/requirements/?branch=master
   :alt: Requirements Status

Molecule is designed to aid in the development and testing of
`Ansible`_ roles including support for multiple instances,
operating system distributions, virtualization providers and test frameworks.

It leverages `Vagrant`_, `Docker`_, `OpenStack`_, and `libvirt`_ to manage
virtual machines/containers, with support for multiple Vagrant providers
(currently VirtualBox, Parallels and VMware Fusion).  Molecule supports
`Serverspec`_ or `Testinfra`_ to run tests.  Molecule uses an `Ansible`_
`playbook`_ (``playbook.yml``), to execute the `role`_ and its tests.

.. _`Ansible`: https://docs.ansible.com
.. _`Test Kitchen`: http://kitchen.ci
.. _`playbook`: https://docs.ansible.com/ansible/playbooks.html
.. _`role`: http://docs.ansible.com/ansible/playbooks_roles.html
.. _`Serverspec`: http://serverspec.org
.. _`Testinfra`: http://testinfra.readthedocs.org
.. _`Vagrant`: http://docs.vagrantup.com/v2
.. _`Docker`: https://www.docker.com
.. _`OpenStack`: https://www.openstack.org
.. _`libvirt`: http://libvirt.org

Ansible Support
---------------

* 1.9.6 - Limited (`Docker`_ provisioner not-supported by `Ansible`_)
* 2.0.2.0 - Supported
* 2.1.1.0 - Supported

Quick Start
-----------

Install molecule using pip:

.. code-block:: bash

  $ pip install molecule

Create a new role with the docker provisioner:

.. code-block:: bash

  $ molecule init foo --docker
  --> Initializing role foo...
  Successfully initialized new role in ./foo


Or add molecule to an existing role:

.. code-block:: bash

  $ cd foo
  $ molecule init --docker
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
  --> Executing testinfra tests found in tests/.
  ============================= test session starts ==============================
  platform darwin -- Python 2.7.11, pytest-2.9.2, py-1.4.31, pluggy-0.3.1
  rootdir: /private/tmp/foo/tests, inifile:
  plugins: mock-1.1, xdist-1.14, testinfra-1.3.1
  collected 2 itemss

  tests/test_default.py ..

  =========================== 2 passed in 1.11 seconds ===========================
  No serverspec tests found in spec/.
  --> Destroying instances ...
  Stopping container foo-01 ...
  Removed container foo-01.
  Stopping container foo-02 ...
  Removed container foo-02.

Documentation
-------------

http://molecule.readthedocs.org/en/latest/

License
-------

MIT

The logo is licensed under the `Creative Commons NoDerivatives 4.0 License`_.  If you have some other use in mind, contact us.

.. _`Creative Commons NoDerivatives 4.0 License`: https://creativecommons.org/licenses/by-nd/4.0/
