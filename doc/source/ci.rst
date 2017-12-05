Continuous integration
----------------------

Travis CI
^^^^^^^^^

`Travis`_ is a CI platform, which can be used to test Ansible roles.

A ``.travis.yml`` testing a role named foo1 with the Docker driver.

.. code-block:: yaml

    ---
    sudo: required
    language: python
    services:
      - docker
    before_install:
      - sudo apt-get -qq update
    install:
      - pip install molecule
      # - pip install required driver (e.g. docker, python-vagrant, shade, boto, apache-libcloud)
    script:
      - molecule test

A ``.travis.yml`` using `Tox`_ as described below.

.. code-block:: yaml

    ---
    sudo: required
    language: python
    services:
      - docker
    before_install:
      - sudo apt-get -qq update
    install:
      - pip install tox-travis
    script:
      - tox

Tox
^^^

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

    $ tox -l
    py27-ansible20
    py27-ansible21
    py27-ansible22

Detox
^^^^^

`Detox`_ is a distributed version of Tox which can be used to make efficient
use of multiple CPUs. Detox will run tox environment tests in parallel.

Detox takes the same arguments and configuration as tox, however Molecule must
be made aware of the parallel testing by setting a MOLECULE_EPHEMERAL_DIRECTORY
environment variable per environment.

.. code-block:: ini

    [tox]
    minversion = 1.8
    envlist = py{27}_ansible{23,24}
    skipsdist = true

    [testenv]
    deps =
        -rrequirements.txt
        ansible23: ansible==2.3
        ansible24: ansible==2.4
    commands =
        molecule test
    setenv =
        MOLECULE_EPHEMERAL_DIRECTORY={envname}

If you are utilizing the Openstack driver you will have to make sure that your
``envname`` variable does not contain any invalid characters, particularly
``-``.

You also must include the MOLECULE_EPHEMERAL_DIRECTORY variable in the
``molecule.yml`` configuration file.

.. code-block:: yaml

    ---
    dependency:
      name: galaxy
    driver:
      name: docker
    lint:
      name: yamllint
    platforms:
      - name: instance1-$MOLECULE_EPHEMERAL_DIRECTORY
        image: mariadb
      - name: instance2-$MOLECULE_EPHEMERAL_DIRECTORY
        image: retr0h/centos7-systemd-ansible:latest
        privileged: True
        command: /usr/sbin/init
    provisioner:
      name: ansible
      lint:
        name: ansible-lint
    scenario:
      name: default
    verifier:
      name: testinfra
      lint:
        name: flake8

.. _`Factors`: http://tox.readthedocs.io/en/latest/config.html#factors-and-factor-conditional-settings
.. _`Travis`: https://travis-ci.org/
.. _`Tox`: https://tox.readthedocs.io/en/lates
.. _`Detox`: https://pypi.python.org/pypi/detox
