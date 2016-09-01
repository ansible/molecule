*********
Verifiers
*********

Molecule is `opinionated`.  By being opinionated molecue tries to enforce a
common way in which roles are maintained.

Testinfra
=========

`Testinfra`_ is the default integration testing framework.  The tests are
linted with `Flake8`_.  Flake8 supports storing its configuration in the
project root as ``.flake8``.

Example files are created with ``molecule init``.

Usage
-----

.. code-block:: yaml

    role_name/
    ├── ...
    └── tests/
        └── test_*.py

.. _`Testinfra`: http://testinfra.readthedocs.org
.. _`Flake8`: http://flake8.pycqa.org/en/latest/

Serverspec
==========

The tests are linted with `Rubocop`_.  `Rubocop`_ supports storing its
configuration in the project root as ``.rubocop.yml``.

Example files are created with ``molecule init --serverspec``.

Usage
-----

.. code-block:: yaml

    role_name/
    ├── ...
    └── spec/
        ├── spec_helper.rb
        └── default_spec.rb

When using serverspec, it's possible to target tests at the following levels:
all instances, specific groups, specific instances.

All files matching the pattern ``spec/*_spec.rb`` will be run against every
instance.

Tests located in ``spec/hosts/<hostname>/*_spec.rb`` will be run against the
specific instance with the given hostname.

Tests located in ``spec/groups/<groupname>/*_spec.rb`` will be run against the
instances in the given group.

For convenience a Gemfile is provided in the root of molecule, which includes
the necessary serverspec dependencies.  See `.travis.yml` for usage.

.. _`Rake`: https://github.com/ruby/rake
.. _`Rubocop`: https://github.com/bbatsov/rubocop
.. _`Serverspec`: http://serverspec.org

Goss
====

`Goss`_ is a YAML based serverspec-like tool for validating a server’s
configuration.

Goss is a bit different than the other verifiers.  The test files must exist
on the system executing ``goss validate``.  Molecule executes a test playbook
which is responsible for installing goss, and distributing tests to the
appropriate ansible hosts/groups.

Example files are created with ``molecule init --goss``.

.. warning:: Concider this verifier experimental.

Usage
-----

.. code-block:: yaml

    role_name/
    ├── ...
    └── files/
        └── goss/
            └── \*.yml
    └── tests/
        └── test_default.yml

.. _`Goss`: https://github.com/aelsabbahy/goss

Trailing
========

Trailing whitespace and newline verifiers are executed on files in the project
root.  The trailing verifiers will ignore the following directories.

.. code-block:: yaml

  molecule:
    ignore_paths:
      - .git
      - .vagrant
      - .molecule

Ansible Lint
============

`Ansible Lint`_ checks playbooks for practices, and behaviour that could
potentially be improved.

.. _`Ansible Lint`: https://github.com/willthames/ansible-lint
