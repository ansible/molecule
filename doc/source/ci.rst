Continuous integration
----------------------

Travis CI
^^^^^^^^^

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
    # - pip install required driver (e.g. docker, python-vagrant, shade)
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

  [jodewey:~/git/ansible-etcd] master+ ± tox -l
  py27-ansible20
  py27-ansible21
  py27-ansible22

.. _`Factors`: http://tox.readthedocs.io/en/latest/config.html#factors-and-factor-conditional-settings
.. _`Travis`: https://travis-ci.org/
.. _`Tox`: https://tox.readthedocs.io/en/latest
