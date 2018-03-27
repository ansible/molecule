********
Examples
********

A good source of examples are the `scenario`_ functional tests.

.. _`scenario`: https://github.com/metacloud/molecule/tree/master/test/scenarios/driver

Docker
======

Molecule can be executed via an Alpine Linux container by leveraging dind
(Docker in Docker).  Currently, we only build images for the latest version
of Ansible and Molecule.  In the future we may break this out into Molecule/
Ansible versioned pairs.  The images are located on `Docker Hub`_.

To test a role, change directory into the role to test, and execute Molecule as
follows.

.. code-block:: bash

    docker run --rm -it \
        -v '$(pwd)':/tmp/$(basename "${PWD}") \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -w /tmp/$(basename "${PWD}") \
        retr0h/molecule:latest \
        sudo molecule test

.. _`Docker Hub`: https://hub.docker.com/r/retr0h/molecule/

Monolith Repo
=============

Molecule is generally used to test roles in isolation.  However, it can also
test roles from a monolith repo.

::

    $ tree monolith-repo -L 3 --prune
    monolith-repo
    ├── library
    │   └── foo.py
    ├── plugins
    │   └── filters
    │       └── foo.py
    └── roles
        ├── bar
        │   └── README.md
        ├── baz
        │   └── README.md
        └── foo
            └── README.md

The role initialized with Molecule (baz in this case) would simply reference
the dependant roles via it's `playbook.yml` or meta dependencies.

Molecule can test complex scenarios leveraging this technique.

.. code-block:: bash

    $ cd monolith-repo/roles/baz
    $ molecule test

Molecule is simply setting the `ANSIBLE_*` environment variables.  To view the
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

Molecule can be customized any number of ways.  Updating the provisioner's env
section in `molecule.yml` to suit the needs of the developer and layout of the
project.

.. code-block:: yaml

    provisioner:
      name: ansible
      env:
        ANSIBLE_$VAR: $VALUE

Systemd Container
=================

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

.. code-block:: bash

    platforms:
      - name: instance
        image: solita/ubuntu-systemd:latest
        privileged: True
        command: /sbin/init

.. [1] https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux_atomic_host/7/html/managing_containers/using_systemd_with_containers
.. [2] https://blog.docker.com/2013/09/docker-can-now-run-within-docker/
.. [3] https://groups.google.com/forum/#!topic/docker-user/RWLHyzg6Z78

Vagrant Proxy Settings
======================

One way of passing in proxy settings to the Vagrant provider is using the
vagrant-proxyconf plugin and adding the vagrant-proxyconf configurations to
~/.vagrant.d/Vagrantfile.

To install the plugin run:

.. code-block:: bash

    $ vagrant plugin install vagrant-proxyconf

On linux add the following Vagrantfile to ~/.vagrant.d/Vagrantfile.

.. code-block:: ruby

    Vagrant.configure("2") do |config|
      if Vagrant.has_plugin?("vagrant-proxyconf")
        config.proxy.http     = ENV['HTTP_PROXY']
        config.proxy.https    = ENV['HTTP_PROXY']
        config.proxy.no_proxy = ENV['NO_PROXY']
      end
    end

Sharing Across Scenarios
========================

Playbooks and tests can be shared across scenarios.

::

    $ tree shared-tests
    shared-tests
    ├── molecule
    │   ├── centos
    │   │   └── molecule.yml
    │   ├── resources
    │   │   ├── playbooks
    │   │   │   ├── Dockerfile.j2
    │   │   │   ├── create.yml
    │   │   │   ├── destroy.yml
    │   │   │   ├── playbook.yml
    │   │   │   └── prepare.yml
    │   │   └── tests
    │   │       └── test_default.py
    │   ├── ubuntu
    │   │   └── molecule.yml
    │   └── ubuntu-upstart
    │       └── molecule.yml

Tests can be shared across scenarios.  In this example the `tests` directory
lives in a shared location and `molecule.yml` is points to the shared tests.

.. code-block:: yaml

    verifier:
    name: testinfra
    directory: ../resources/tests/
    lint:
      name: flake8
