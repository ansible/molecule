*************************
Common Molecule Use Cases
*************************

.. _docker-usage-example:

Running inside a container
==========================

Molecule is built into a Docker image by the `Toolset`_ project.

Any questions or bugs related to use of Molecule from within a container
should be addressed by the Toolset project.

.. _`Toolset`: https://github.com/ansible-community/toolset

Docker With Non-Privileged User
===============================

The default Molecule Docker driver executes Ansible playbooks as the root user.
If your workflow requires a non-privileged user, then adapt ``molecule.yml``
and ``Dockerfile.j2`` as follows.

Append the following code block to the end of ``Dockerfile.j2``. It creates an ``ansible``
user with passwordless sudo privileges.

The variable ``SUDO_GROUP`` depends on the target distribution. ``centos:8`` uses ``wheel``.

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

Modify ``provisioner.inventory`` in ``molecule.yml`` as follows:

.. code-block:: yaml

    platforms:
      - name: instance
        image: centos:8
        # …

.. code-block:: yaml

    provisioner:
      name: ansible
      # …
      inventory:
        host_vars:
          # setting for the platform instance named 'instance'
          instance:
            ansible_user: ansible

Make sure to use your **platform instance name**.  In this case ``instance``.

An example for a different platform instance name:

.. code-block:: yaml

    platforms:
      - name: centos8
        image: centos:8
        # …

.. code-block:: yaml

    provisioner:
      name: ansible
      # …
      inventory:
        host_vars:
          # setting for the platform instance named 'centos8'
          centos8:
            ansible_user: ansible

To test it, add the following task to ``tasks/main.yml``. It fails, because the
non-privileged user is not allowed to create a folder in ``/opt/``.
This needs to be performed using ``sudo``.

To perform the task using ``sudo``, uncomment ``become: yes``.
Now the task will succeed.

.. code-block:: yaml

    - name: Create apps dir
      file:
        path: /opt/examples
        owner: ansible
        group: deployer
        mode: 0775
        state: directory
      # become: yes

Don't forget to run ``molecule destroy`` if image has already been created.

Podman inside Docker
====================

Sometimes your CI system comes prepared to run with Docker but you want to
test podman into it. This ``prepare.yml`` playbook would let podman run inside
a privileged Docker host by adding some required settings:

.. code-block:: yaml

    - name: prepare
      hosts: podman-in-docker
      tasks:
        - name: install fuse-overlayfs
          package:
            name:
              - fuse-overlayfs

        - name: create containers config dir
          file:
            group: root
            mode: a=rX,u+w
            owner: root
            path: /etc/containers
            state: directory

        - name: make podman use fuse-overlayfs storage
          copy:
            content: |
              # See man 5 containers-storage.conf for more information
              [storage]
              driver = "overlay"
              [storage.options.overlay]
              mount_program = "/usr/bin/fuse-overlayfs"
              mountopt = "nodev,metacopy=on"
            dest: /etc/containers/storage.conf
            group: root
            mode: a=r,u+w
            owner: root

        - name: make podman use cgroupfs cgroup manager
          copy:
            content: |
              # See man 5 libpod.conf for more information
              cgroup_manager = "cgroupfs"
            dest: /etc/containers/libpod.conf
            group: root
            mode: a=r,u+w
            owner: root

Another option is to configure the same settings directly into the ``molecule.yml``
definition:

.. code-block:: yaml

        driver:
          name: podman
        platforms:
          - name: podman-in-docker
            # ... other options
            cgroup_manager: cgroupfs
            storage_opt: overlay.mount_program=/usr/bin/fuse-overlayfs
            storage_driver: overlay

At the time of writing, `Gitlab CI shared runners run privileged Docker hosts
<https://docs.gitlab.com/ee/user/gitlab_com/#shared-runners>`__
and are suitable for these workarounds.

Systemd Container
=================

To start a service which requires systemd, `in a non-privileged container`_,
configure ``molecule.yml`` with a systemd compliant image, tmpfs, volumes,
and command as follows.

.. code-block:: yaml

    platforms:
      - name: instance
        image: centos:8
        command: /sbin/init
        tmpfs:
          - /run
          - /tmp
        volumes:
          - /sys/fs/cgroup:/sys/fs/cgroup:ro

Note that centos:8 image contains a `seccomp security profile for Docker`_ which enables the use of systemd.
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
by either giving it ``SYS_ADMIN`` capabilities or running it in ``privileged`` mode.

.. important::

    Use caution when using ``privileged`` mode or ``SYS_ADMIN``
    capabilities as it grants the container elevated access to the
    underlying system.

To limit the scope of the extended privileges, grant ``SYS_ADMIN``
capabilities along with the same image, command, and volumes as shown in the ``non-privileged`` example.

.. code-block:: yaml

    platforms:
      - name: instance
        image: centos:8
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
        image: centos:8
        command: /sbin/init
        privileged: True

.. _`seccomp security profile for Docker`: https://docs.docker.com/engine/security/seccomp/
.. _`the one available in fedora`: https://src.fedoraproject.org/rpms/docker/raw/88fa030b904d7af200b150e10ea4a700f759cca4/f/seccomp.json
.. _`in a non-privileged container`: https://developers.redhat.com/blog/2016/09/13/running-systemd-in-a-non-privileged-container/
.. _`start the container with extended privileges`: https://blog.docker.com/2013/09/docker-can-now-run-within-docker/

Monolith Repo
=============

Molecule is generally used to test roles in isolation.  However, it can also
test roles from a monolith repo.

.. code-block: bash

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
the dependent roles via it's ``converge.yml`` or meta dependencies.

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


Sharing Across Scenarios
========================

Playbooks and tests can be shared across scenarios.

.. code-block:: bash

    $ tree shared-tests
    shared-tests
    ├── molecule
    │   ├── centos
    │   │   └── molecule.yml
    │   ├── resources
    │   │   ├── playbooks
    │   │   │   ├── Dockerfile.j2 (optional)
    │   │   │   ├── create.yml
    │   │   │   ├── destroy.yml
    │   │   │   ├── converge.yml  # <-- previously called playbook.yml
    │   │   │   └── prepare.yml
    │   │   └── tests
    │   │       └── test_default.py
    │   ├── ubuntu
    │   │   └── molecule.yml
    │   └── ubuntu-upstart
    │       └── molecule.yml

Tests and playbooks can be shared across scenarios.

In this example the `tests` directory lives in a shared
location and ``molecule.yml`` points to the shared tests.

.. code-block:: yaml

    verifier:
      name: testinfra
      directory: ../resources/tests/

In this second example the actions `create`, `destroy`,
`converge` and `prepare` are loaded from a shared directory.

.. code-block:: yaml

    provisioner:
      name: ansible
      playbooks:
        create: ../resources/playbooks/create.yml
        destroy: ../resources/playbooks/destroy.yml
        converge: ../resources/playbooks/converge.yml
        prepare: ../resources/playbooks/prepare.yml

.. _parallel-usage-example:

Running Molecule processes in parallel mode
===========================================

.. important::

    This functionality should be considered experimental. It is part of ongoing
    work towards enabling parallelizable functionality across all moving parts
    in the execution of the Molecule feature set.

.. note::

    Only the following sequences support parallelizable functionality:

      * ``check_sequence``: ``molecule check --parallel``
      * ``destroy_sequence``: ``molecule destroy --parallel``
      * ``test_sequence``: ``molecule test --parallel``

    It is currently only available for use with the Docker driver.

When Molecule receives the ``--parallel`` flag it will generate a `UUID`_ for
the duration of the testing sequence and will use that unique identifier to
cache the run-time state for that process. The parallel Molecule processes
cached state and created instances will therefore not interfere with each
other.

Molecule uses a new and separate caching folder for this in the
``$HOME/.cache/molecule_parallel`` location. Molecule exposes a new environment
variable ``MOLECULE_PARALLEL`` which can enable this functionality.

It is possible to run Molecule processes in parallel using another tool to
orchestrate the parallelization (such as `GNU Parallel`_ or `Pytest`_).
If you do so, make sure Molecule knows it is running in parallel mode by
specifying the ``--parallel`` flag to your command(s) to avoid concurrency
issues.

.. _GNU Parallel: https://www.gnu.org/software/parallel/
.. _Pytest: https://docs.pytest.org/en/latest/
.. _UUID: https://en.wikipedia.org/wiki/Universally_unique_identifier
