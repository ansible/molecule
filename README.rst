********
Molecule
********

.. image:: https://badge.fury.io/py/molecule.svg
   :target: https://badge.fury.io/py/molecule
   :alt: PyPI Package

.. image:: https://readthedocs.org/projects/molecule/badge/?version=latest
   :target: https://molecule.readthedocs.io/en/latest/
   :alt: Documentation Status

.. image:: https://img.shields.io/badge/license-MIT-brightgreen.svg
   :target: LICENSE
   :alt: Repository License

Molecule is designed to aid in the development and testing of `Ansible`_ roles
including support for multiple instances, operating system distributions,
virtualization providers, scenarios, and test frameworks.

Molecule uses `Ansible`_ `playbooks`_ to exercise the `role`_ and its
associated tests.  Molecule supports any provider [#]_ `Ansible`_ supports.

.. [#]

   This could be bare metal, virtual, cloud, or containers.  So long as
   accessbible through an Ansible supported connection.  Molecule simply
   leverages Ansible's module system to manage instances.

.. _`playbooks`: https://docs.ansible.com/ansible/playbooks.html
.. _`role`: http://docs.ansible.com/ansible/playbooks_roles.html

Documentation
=============

https://molecule.readthedocs.io/

Ansible Support
===============

* 2.2.0.0 - Supported

Requirements
============

Molecule relies on several outside packages and programs to function.

Dependency
----------

* `Ansible Galaxy`_

Driver
------

* `Docker`_

Lint
----

* `Ansible Lint`_

Provisioner
-----------

* `Ansible`_

Verifier
--------

* `Testinfra`_

.. _`Ansible Galaxy`: http://docs.ansible.com/ansible/galaxy.html
.. _`Docker`: https://www.docker.com
.. _`Ansible Lint`: https://github.com/willthames/ansible-lint
.. _`Ansible`: https://docs.ansible.com
.. _`Testinfra`: https://testinfra.readthedocs.io

Quick Start
===========

Install Molecule using pip:

.. code-block:: bash

  $ pip install ansible
  $ pip install molecule --pre

Create a new role with the docker driver:

.. code-block:: bash

  $ molecule init --role foo --driver docker
  --> Initializing role foo...
  Successfully initialized new role in /private/tmp/foo.

Or add Molecule to an existing role:

.. code-block:: bash

  $ cd foo
  $ molecule init --driver docker
  --> Initializing molecule in current directory...
  Successfully initialized new role in /private/tmp/foo.

Update the role with needed functionality and tests.  Now test it:

.. code-block:: bash

  $ cd foo
  $ molecule test
  ...

License
=======

MIT

The logo is licensed under the `Creative Commons NoDerivatives 4.0 License`_.  If you have some other use in mind, contact us.

.. _`Creative Commons NoDerivatives 4.0 License`: https://creativecommons.org/licenses/by-nd/4.0/
