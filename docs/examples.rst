********
Examples
********

A good source of examples are the `scenario`_ functional tests.

.. _`scenario`: https://github.com/ansible/molecule/tree/master/test/scenarios/driver

.. _docker-usage-example:

Docker
======

Molecule can be executed via an Alpine Linux container by leveraging dind
(Docker in Docker).  Currently, we only build images for the latest version
of Ansible and Molecule.  In the future we may break this out into Molecule/
Ansible versioned pairs.  The images are located on `quay.io`_.

To test a role, change directory into the role to test, and execute Molecule as
follows.

.. code-block:: bash

    docker run --rm -it \
        -v "$(pwd)":/tmp/$(basename "${PWD}"):ro \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -w /tmp/$(basename "${PWD}") \
        quay.io/ansible/molecule:2.20 \
        molecule test

.. _`quay.io`: https://quay.io/repository/ansible/molecule

Docker With Non-Privileged User
===============================

Default Molecule Docker driver execute Ansible playbooks with root user. If your
workflow require non-privileged user, some simple changes to ``molecule.yaml``
and ``Dockerfile.j2`` are required.

Append to end off ``Dockerfile.j2`` commands that are creating ``ansible``
user with passwordless sudo privileges. Variable ``SUDO_GROUP`` depends on distribution
``wheel`` is used on ``centos:7``.

.. code-block:: docker

    # Create `ansible` user with sudo permissions and membership in `DEPLOY_GROUP`
    ENV ANSIBLE_USER=ansible SUDO_GROUP=wheel DEPLOY_GROUP=deployer
    RUN set -xe \
      && groupadd -r ${ANSIBLE_USER} \
      && groupadd -r ${DEPLOY_GROUP} \
      && useradd -m -g ${ANSIBLE_USER} ${ANSIBLE_USER} \
      && usermod -aG ${SUDO_GROUP} ${ANSIBLE_USER} \
      && usermod -aG ${DEPLOY_GROUP} ${ANSIBLE_USER} \
      && sed -i "/^%${SUDO_GROUP}/s/ALL\$/NOPASSWD:ALL/g" /etc/sudoers

Change ``molecule.yaml`` file by modifying ``provisioner`` block and changing
default provisioning user from root to newly created one.

.. code-block:: yaml

    provisioner:
      name: ansible
      lint:
        name: ansible-lint
      inventory:
        host_vars:
          instance:
            ansible_user: ansible

Now you can test new user with simple task add following TASK to ``tasks/main.yml`` it
should fail until you uncomment ``become: yes``.

.. code-block:: yaml

    - name: Create apps dir
      file:
        path: /opt/examples
        owner: ansible
        group: deployer
        mode: 0775
        state: directory
      # become: yes

Don't forget to run ``molecule destroy`` if image vas already created.

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
the dependant roles via it's ``playbook.yml`` or meta dependencies.

Molecule can test complex scenarios leveraging this technique.

.. code-block:: bash

    $ cd monolith-repo/roles/baz
    $ molecule test

Molecule is simply setting the ``ANSIBLE_*`` environment variables.  To view the
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
section in ``molecule.yml`` to suit the needs of the developer and layout of the
project.

.. code-block:: yaml

    provisioner:
      name: ansible
      env:
        ANSIBLE_$VAR: $VALUE

Systemd Container
=================

To start a service which requires systemd, `in a non-privileged container`_,
configure ``molecule.yml`` with a systemd compliant image, tmpfs, volumes,
and command as follows.

.. code-block:: yaml

    platforms:
      - name: instance
        image: centos:7
        command: /sbin/init
        tmpfs:
          - /run
          - /tmp
        volumes:
          - /sys/fs/cgroup:/sys/fs/cgroup:ro

Note that centos:7 image contains a `seccomp security profile for Docker`_ which enables the use of systemd.
When needed, such security profiles can be reused (for example `the one available in Fedora`_):

.. code-block:: yaml

    platforms:
      - name: instance
        image: debian:stretch
        command: /sbin/init
        security_opts:
          - seccomp=path/to/seccomp.json
        tmpfs:
          - /run
          - /tmp
        volumes:
          - /sys/fs/cgroup:/sys/fs/cgroup:ro

The developer can also opt to `start the container with extended privileges`_,
by either giving it ``SYS_ADMIN`` capabilites or running it in ``privileged`` mode.

.. important::

    Use caution when using ``privileged`` mode or ``SYS_ADMIN``
    capabilities as it `grants the container elevated access`_ to the
    underlying system.

To limit the scope of the extended privileges, grant ``SYS_ADMIN``
capabilities along with the same image, command, and volumes as shown in the ``non-privileged`` example.

.. code-block:: yaml

    platforms:
      - name: instance
        image: centos:7
        command: /sbin/init
        capabilities:
          - SYS_ADMIN
        volumes:
          - /sys/fs/cgroup:/sys/fs/cgroup:ro

To start the container in ``privileged`` mode, set the privileged flag along with the
same image and command as shown in the ``non-privileged`` example.

.. code-block:: yaml

    platforms:
      - name: instance
        image: centos:7
        command: /sbin/init
        privileged: True

.. _`seccomp security profile for Docker`: https://docs.docker.com/engine/security/seccomp/
.. _`the one available in fedora`: https://src.fedoraproject.org/rpms/docker/raw/master/f/seccomp.json
.. _`in a non-privileged container`: https://developers.redhat.com/blog/2016/09/13/running-systemd-in-a-non-privileged-container/
.. _`start the container with extended privileges`: https://blog.docker.com/2013/09/docker-can-now-run-within-docker/
.. _`grants the container elevated access`: https://groups.google.com/forum/#!topic/docker-user/RWLHyzg6Z78

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
lives in a shared location and ``molecule.yml`` is points to the shared tests.

.. code-block:: yaml

    verifier:
    name: testinfra
    directory: ../resources/tests/
    lint:
      name: flake8
