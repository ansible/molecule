.. _common-use-cases:

****************
Common Use Cases
****************

Testing an existing role
------------------------

Molecule can be used to test existing roles. We only need to generate a
``molecule`` directory in our existing role directory structure using
the following command:

.. code-block:: bash

    $ molecule init scenario -r my-role-name

This will create the default :ref:`root_scenario`. We can also pass ``-s
my-scenario-name`` in order to create new scenario directory structures.

Testing multiple roles
----------------------

Molecule can be used to test multiple roles in the same directory structure.

If we consider the following layout:

::

    $ tree monolith-repo -L 3 --prune
    monolith-repo
    ├── library
    │   └── foo.py
    ├── plugins
    │   └── filters
    │       └── foo.py
    └── roles
        ├── bar
        │   └── README.md
        ├── baz
        │   └── README.md
        └── foo
            └── README.md

Molecule is simply setting the ``ANSIBLE_*`` environment variables. To view the
environment variables set during a Molecule operation pass the ``--debug``
flag.

.. code-block:: bash

    $ molecule --debug test

    DEBUG: ANSIBLE ENVIRONMENT
    ---
    ANSIBLE_CONFIG: /private/tmp/monolith-repo/roles/baz/molecule/default/.molecule/ansible.cfg
    ANSIBLE_FILTER_PLUGINS: /Users/jodewey/.pyenv/versions/2.7.13/lib/python2.7/site-packages/molecule/provisioner/ansible/plugins/filters:/private/tmp/monolith-repo/roles/baz/plugins/filters:/private/tmp/monolith-repo/roles/baz/molecule/default/.molecule/plugins/filters
    ANSIBLE_LIBRARY: /Users/jodewey/.pyenv/versions/2.7.13/lib/python2.7/site-packages/molecule/provisioner/ansible/plugins/libraries:/private/tmp/monolith-repo/roles/baz/library:/private/tmp/monolith-repo/roles/baz/molecule/default/.molecule/library
    ANSIBLE_ROLES_PATH: /private/tmp/monolith-repo/roles:/private/tmp/monolith-repo/roles/baz/molecule/default/.molecule/roles

Molecule can be customized any number of ways. Updating the provisioner's env
section in ``molecule.yml`` to suit the needs of the developer and layout of
the project.

.. code-block:: yaml

    provisioner:
      name: ansible
      env:
        ANSIBLE_$VAR: $VALUE

Using ``SystemD`` with Docker
-----------------------------

The docker daemon was designed to provide a simple means of starting, stopping
and managing containers. It was not originally designed to bring up an entire
Linux system or manage services for such things as start-up order, dependency
checking, and failed service recovery. [1]_

To start a service which requires systemd, configure `molecule.yml` with a
systemd compliant image, capabilities, volumes, and command as follows.

.. code-block:: yaml

    platforms:
      - name: instance
        image: solita/ubuntu-systemd:latest
        command: /sbin/init
        capabilities:
          - SYS_ADMIN
        volumes:
          - /sys/fs/cgroup:/sys/fs/cgroup:ro

The developer can also opt to start the container with extended privileges.

.. important::

    Use caution when using `privileged` mode. [2]_ [3]_

.. code-block:: yaml

    platforms:
      - name: instance
        image: solita/ubuntu-systemd:latest
        privileged: True
        command: /sbin/init

.. [1] https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux_atomic_host/7/html/managing_containers/using_systemd_with_containers
.. [2] https://blog.docker.com/2013/09/docker-can-now-run-within-docker/
.. [3] https://groups.google.com/forum/#!topic/docker-user/RWLHyzg6Z78

Sharing configuration between roles
-----------------------------------

Playbooks and tests can be shared across scenarios.

::

    $ tree shared-tests
    shared-tests
    ├── molecule
    │   ├── centos
    │   │   └── molecule.yml
    │   ├── resources
    │   │   ├── playbooks
    │   │   │   ├── Dockerfile.j2
    │   │   │   ├── create.yml
    │   │   │   ├── destroy.yml
    │   │   │   ├── playbook.yml
    │   │   │   └── prepare.yml
    │   │   └── tests
    │   │       └── test_default.py
    │   ├── ubuntu
    │   │   └── molecule.yml
    │   └── ubuntu-upstart
    │       └── molecule.yml

Tests can be shared across scenarios. In this example the `tests` directory
lives in a shared location and ``molecule.yml`` is points to the shared tests.

.. code-block:: yaml

    verifier:
    name: testinfra
    directory: ../resources/tests/
    lint:
      name: flake8
