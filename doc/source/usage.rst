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

It is very simple to run tests using the molecule command from the working
directory of your role.

* ``molecule destroy``: Halts and destroys all instances associated with
  current role.
* ``molecule create``: Builds instances specified in molecule.yml.
* ``molecule converge``: Runs playbook.yml against instances associated with
  current role.
* ``molecule idempotence``: Checks output of ansible-playbook for
  "changed"/"failed".
* ``molecule verify``: Runs the functional tests (serverspec, testinfra).
* ``molecule login <host>``: Login to an instance via ssh.
* ``molecule init <role>``: Creates the directory structure and files for a new
  Ansible role compatible with molecule.
* ``molecule test``: Runs a series of commands to create, verify and destroy
  instances.

The exact sequence of commands run during the ``test`` command can be
configured in the `test['sequence']` config option.

The ``test`` command supports a ``--destroy`` argument that will accept the
values always, never, and passing. Use these to tune the behavior for various
use cases.  For example, ``--destroy=always`` might be useful when using
molecule for CI/CD.

Travis CI
=========

`Travis`_ is an excellent CI platform for testing Ansible roles. With the
docker driver, molecule can easily be used to test multiple configurations on
Travis. Here is an example of a ``.travis.yml`` that is used to test a role
named foo1. In this example, the role ``foo1`` uses the docker driver and is
assumed to be in the directory ``roledir/foo1`` with the proper
``molecule.yml``.

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
    - cd roledir/foo1
    - molecule test

.. _`Travis`: https://travis-ci.org/
