*****
Usage
*****

In the contexts of operations and virtualization, the word 'provision' tends to
refer to the initial creation of machines by allocating (hardware) resources;
in contrast, in the context of configuration management (and in vagrant),
'provisioning' refers to taking the (virtual) machine from an initial boot to
having run the configuration management system (Ansible, Salt, Puppet, Chef,
CFEngine or just shell). Molecule uses the term 'converge' (as does Test
Kitchen) to refer to this latter meaning of 'provisioning' (i.e. "Run Ansible
on the new test VM").

It is very simple to run tests using the Molecule command from the working
directory of your role.

See ``molecule --help``

The exact sequence of commands run during the ``test`` command can be
configured in the `test['sequence']` config option.

.. code-block:: yaml

  molecule:
    test:
      sequence:
        - destroy
        - syntax
        - create
        - converge
        - idempotence
        - verify

The ``test`` command will destroy the instance(s) after successful completion
of all test sequences.  The ``test`` command supports a ``--destroy`` argument
that will accept the values `always` (default), `never`, and `passing`.  Use
these to tune the behavior for various use cases.

For example, ``--destroy=always`` might be useful when using Molecule for
CI/CD.

Continuous integration
======================

Travis CI
---------

`Travis`_ is a CI platform, which can be used to test Ansible roles.

A ``.travis.yml`` testing a role named foo1 with the Docker driver.

.. code-block:: yaml

  sudo: required
  language: python
  services:
    - docker
  before_install:
    - sudo apt-get -qq update
    - sudo apt-get install -o Dpkg::Options::="--force-confold" --force-yes -y docker-engine
  install:
    - pip install molecule
  script:
    - molecule test

A ``.travis.yml`` using `Tox`_ as described below.

.. code-block:: yaml

  sudo: required
  language: python
  services:
    - docker
  before_install:
    - sudo apt-get -qq update
    - sudo apt-get install -o Dpkg::Options::="--force-confold" --force-yes -y docker-engine
  install:
    - pip install tox-travis
  script:
    - tox

Tox
---

`Tox`_ is a generic virtualenv management, and test command line tool.  `Tox`_
can be used in conjunction with `Factors`_ and Molecule, to perform scenario
tests.

To test the role against multiple versions of Ansible.

.. code-block:: ini

  [tox]
  minversion = 1.8
  envlist = py{27}-ansible{20,21,22}
  skipsdist = true

  [testenv]
  passenv = *
  deps =
      -rrequirements.txt
      ansible20: ansible==2.0.2.0
      ansible21: ansible==2.1.2.0
      ansible22: ansible==2.2.0.0
  commands =
      molecule test

To view the factor generated tox environments.

.. code-block:: bash

  [jodewey:~/git/ansible-etcd] master+ ± tox -l
  py27-ansible20
  py27-ansible21
  py27-ansible22

.. _`Travis`: https://travis-ci.org/
.. _`Tox`: https://tox.readthedocs.io/en/latest/
.. _`Factors`: http://tox.readthedocs.io/en/latest/config.html#factors-and-factor-conditional-settings
