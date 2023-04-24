# Common Molecule Use Cases

## Running inside a container

Molecule is built into a Docker image by the [Ansible Creator Execution
Environment](https://github.com/ansible/creator-ee) project.

Any questions or bugs related to use of Molecule from within a container
should be addressed by the Ansible Creator Execution Environment
project.

## Customizing the Docker Image Used by a Scenario/Platform

The docker driver supports using pre-built images and `docker build`
-ing local customizations for each scenario's platform. The Docker
image used by a scenario is governed by the following configuration
items:

1.  `platforms[*].image`: Docker image name:tag to use as base image.

2.  `platforms[*].pre_build_image`: Whether to customize base image or
    use as-is[^1].

    > - When `true`, use the specified `platform[].image` as-is.
    >
    > - When `false`, exec `docker build` to customize base image
    >   using either:
    >
    >   > - Dockerfile specified by `platforms[*].dockerfile` or
    >   > - Dockerfile rendered from `Dockerfile.j2` template (in
    >   >   scenario dir)

The `Dockerfile.j2` template is generated at
`molecule init scenario`-time when `--driver-name` is `docker`. The
template can be customized as needed to create the desired modifications
to the Docker image used in the scenario.

Note: `platforms[*].pre_build_image` defaults to `true` in each
scenario's generated `molecule.yml` file.

## Docker With Non-Privileged User

The default Molecule Docker driver executes Ansible playbooks as the
root user. If your workflow requires adding support for running as a
non-privileged user, then adapt `molecule.yml` and `Dockerfile.j2` as
follows.

Note: The `Dockerfile` templating and image building processes are only
done for scenarios with `pre_build_image = False`, which is not the
default setting in generated `molecule.yml` files.

To modify the Docker image to support running as normal user:

Append the following code block to the end of `Dockerfile.j2`. It
creates an `ansible` user with passwordless sudo privileges. Note the
variable `SUDO_GROUP` depends on the target distribution[^2].

```docker
# Create `ansible` user with sudo permissions and membership in `DEPLOY_GROUP`
# This template gets rendered using `loop: "{{ molecule_yml.platforms }}"`, so
# each `item` is an element of platforms list from the molecule.yml file for this scenario.
ENV ANSIBLE_USER=ansible DEPLOY_GROUP=deployer
ENV SUDO_GROUP={{'sudo' if 'debian' in item.image else 'wheel' }}
RUN set -xe \
  && groupadd -r ${ANSIBLE_USER} \
  && groupadd -r ${DEPLOY_GROUP} \
  && useradd -m -g ${ANSIBLE_USER} ${ANSIBLE_USER} \
  && usermod -aG ${SUDO_GROUP} ${ANSIBLE_USER} \
  && usermod -aG ${DEPLOY_GROUP} ${ANSIBLE_USER} \
  && sed -i "/^%${SUDO_GROUP}/s/ALL\$/NOPASSWD:ALL/g" /etc/sudoers
```

Modify `provisioner.inventory` in `molecule.yml` as follows:

```yaml
platforms:
  - name: instance
    image: quay.io/centos/centos:stream8
    # …
```

```yaml
provisioner:
  name: ansible
  # …
  inventory:
    host_vars:
      # setting for the platform instance named 'instance'
      instance:
        ansible_user: ansible
```

Make sure to use your **platform instance name**. In this case
`instance`.

An example for a different platform instance name:

```yaml
platforms:
  - name: centos8
    image: quay.io/centos/centos:stream8
    # …
```

```yaml
provisioner:
  name: ansible
  # …
  inventory:
    host_vars:
      # setting for the platform instance named 'centos8'
      centos8:
        ansible_user: ansible
```

To test it, add the following task to `tasks/main.yml`. It fails,
because the non-privileged user is not allowed to create a folder in
`/opt/`. This needs to be performed using `sudo`.

To perform the task using `sudo`, uncomment `become: yes`. Now the task
will succeed.

```yaml
- name: Create apps dir
  file:
    path: /opt/examples
    owner: ansible
    group: deployer
    mode: 0775
    state: directory
  # become: yes
```

Don't forget to run `molecule destroy` if image has already been
created.

# Podman inside Docker

Sometimes your CI system comes prepared to run with Docker but you want
to test podman into it. This `prepare.yml` playbook would let podman run
inside a privileged Docker host by adding some required settings:

```yaml
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
```

Another option is to configure the same settings directly into the
`molecule.yml` definition:

```yaml
driver:
  name: podman
platforms:
  - name: podman-in-docker
    # ... other options
    cgroup_manager: cgroupfs
    storage_opt: overlay.mount_program=/usr/bin/fuse-overlayfs
    storage_driver: overlay
```

At the time of writing, [Gitlab CI shared runners run privileged Docker
hosts](https://docs.gitlab.com/ee/user/gitlab_com/#shared-runners) and
are suitable for these workarounds.

## Systemd Container

To start a service which requires systemd, [in a non-privileged
container](https://developers.redhat.com/blog/2016/09/13/running-systemd-in-a-non-privileged-container/),
configure `molecule.yml` with a systemd compliant image, tmpfs, volumes,
and command as follows.

```yaml
platforms:
  - name: instance
    image: quay.io/centos/centos:stream8
    command: /sbin/init
    tmpfs:
      - /run
      - /tmp
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:ro
```

When needed, such security profiles can be reused (for example [the one
available in
Fedora](https://src.fedoraproject.org/rpms/docker/raw/88fa030b904d7af200b150e10ea4a700f759cca4/f/seccomp.json)):

```yaml
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
```

The developer can also opt to [start the container with extended
privileges](https://blog.docker.com/2013/09/docker-can-now-run-within-docker/),
by either giving it `SYS_ADMIN` capabilities or running it in
`privileged` mode.

!!! warning

    Use caution when using `privileged` mode or `SYS_ADMIN` capabilities as
    it grants the container elevated access to the underlying system.

To limit the scope of the extended privileges, grant `SYS_ADMIN`
capabilities along with the same image, command, and volumes as shown in
the `non-privileged` example.

```yaml
platforms:
  - name: instance
    image: quay.io/centos/centos:stream8
    command: /sbin/init
    capabilities:
      - SYS_ADMIN
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:ro
```

To start the container in `privileged` mode, set the privileged flag
along with the same image and command as shown in the `non-privileged`
example.

```yaml
platforms:
  - name: instance
    image: quay.io/centos/centos:stream8
    command: /sbin/init
    privileged: True
```

## Monolith Repo

Molecule is generally used to test roles in isolation. However, it can
also test roles from a monolith repo.

```bash
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
```

The role initialized with Molecule (baz in this case) would simply
reference the dependent roles via it's `converge.yml` or meta
dependencies.

Molecule can test complex scenarios leveraging this technique.

```bash
$ cd monolith-repo/roles/baz
$ molecule test
```

Molecule is simply setting the `ANSIBLE_*` environment variables. To
view the environment variables set during a Molecule operation pass the
`--debug` flag.

```bash
$ molecule --debug test

DEBUG: ANSIBLE ENVIRONMENT
---
ANSIBLE_CONFIG: /private/tmp/monolith-repo/roles/baz/molecule/default/.molecule/ansible.cfg
ANSIBLE_FILTER_PLUGINS: /Users/jodewey/.pyenv/versions/2.7.13/lib/python2.7/site-packages/molecule/provisioner/ansible/plugins/filters:/private/tmp/monolith-repo/roles/baz/plugins/filters:/private/tmp/monolith-repo/roles/baz/molecule/default/.molecule/plugins/filters
ANSIBLE_LIBRARY: /Users/jodewey/.pyenv/versions/2.7.13/lib/python2.7/site-packages/molecule/provisioner/ansible/plugins/libraries:/private/tmp/monolith-repo/roles/baz/library:/private/tmp/monolith-repo/roles/baz/molecule/default/.molecule/library
ANSIBLE_ROLES_PATH: /private/tmp/monolith-repo/roles:/private/tmp/monolith-repo/roles/baz/molecule/default/.molecule/roles
```

Molecule can be customized any number of ways. Updating the
provisioner's env section in `molecule.yml` to suit the needs of the
developer and layout of the project.

```yaml
provisioner:
  name: ansible
  env:
    ANSIBLE_$VAR: $VALUE
```

## Sharing Across Scenarios

Playbooks and tests can be shared across scenarios.

```bash
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
```

Tests and playbooks can be shared across scenarios.

In this example the `tests` directory lives in a shared
location and `molecule.yml` points to the shared tests.

```yaml
verifier:
  name: testinfra
  directory: ../resources/tests/
```

In this second example the actions `create`,
`destroy`, `converge` and `prepare`
are loaded from a shared directory.

```yaml
provisioner:
  name: ansible
  playbooks:
    create: ../resources/playbooks/create.yml
    destroy: ../resources/playbooks/destroy.yml
    converge: ../resources/playbooks/converge.yml
    prepare: ../resources/playbooks/prepare.yml
```

## Running Molecule processes in parallel mode

!!! warning

    This functionality should be considered experimental. It is part of
    ongoing work towards enabling parallelizable functionality across all
    moving parts in the execution of the Molecule feature set.

!!! note

    Only the following sequences support parallelizable functionality:

    > -   `check_sequence`: `molecule check --parallel`
    > -   `destroy_sequence`: `molecule destroy --parallel`
    > -   `test_sequence`: `molecule test --parallel`

    It is currently only available for use with the Docker driver.

When Molecule receives the `--parallel` flag it will generate a
[UUID](https://en.wikipedia.org/wiki/Universally_unique_identifier) for
the duration of the testing sequence and will use that unique identifier
to cache the run-time state for that process. The parallel Molecule
processes cached state and created instances will therefore not
interfere with each other.

Molecule uses a new and separate caching folder for this in the
`$HOME/.cache/molecule_parallel` location. Molecule exposes a new
environment variable `MOLECULE_PARALLEL` which can enable this
functionality.

It is possible to run Molecule processes in parallel using another tool
to orchestrate the parallelization (such as [GNU
Parallel](https://www.gnu.org/software/parallel/) or
[Pytest](https://docs.pytest.org/en/latest/)). If you do so, make sure
Molecule knows it is running in parallel mode by specifying the
`--parallel` flag to your command(s) to avoid concurrency issues.

[^1]:
    [Implementation in molecule docker
    driver](https://github.com/ansible-community/molecule-plugins/blob/main/src/molecule_plugins/docker/playbooks/create.yml)

[^2]: Debian uses `sudo` instead of [wheel group.](https://wiki.debian.org/sudo/)
