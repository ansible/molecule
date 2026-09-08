# Test a role

Use this page when the main question is whether a role produces the expected result. It shows how to create a Molecule scenario, provision a disposable test instance, apply the role, and verify its result.

## Prerequisites

Install:

- [Ansible](https://docs.ansible.com/projects/ansible/latest/installation_guide/intro_installation.html)
- [Molecule](https://docs.ansible.com/projects/molecule/installation/)
- [Podman](https://podman.io/getting-started/installation)

The example uses the `containers.podman` collection for the container lifecycle and connection plugin. Molecule installs it from the scenario requirements file during the dependency sequence.

## Create a role

Create a role directory and initialize its default Molecule scenario:

```bash
mkdir -p my_role/tasks
cd my_role
molecule init scenario default
```

Add a small task to `tasks/main.yml`:

```yaml
---
- name: Create a marker file
  ansible.builtin.copy:
    content: molecule role test
    dest: /tmp/molecule_role_marker
    mode: "0644"
```

The example uses a disposable container. The role under test writes a marker file into that container, and `verify.yml` checks that the file exists.

## Scenario layout

After completing the steps below, the completed scenario will have this structure:

```text
my_role/
├── tasks/
│   └── main.yml
└── molecule/
    └── default/
        ├── molecule.yml
        ├── requirements.yml
        ├── inventory/
        │   └── hosts.yml
        ├── create.yml
        ├── converge.yml
        ├── verify.yml
        └── destroy.yml
```

The `molecule/` directory and its scenario files are added for testing. They are not part of the role itself.

## Configure the scenario

Set the test sequence and Ansible inventory in `molecule/default/molecule.yml`:

```yaml
---
ansible:
  cfg:
    defaults:
      deprecation_warnings: false
      roles_path: ${MOLECULE_PROJECT_DIRECTORY}/../
  executor:
    args:
      ansible_playbook:
        - --inventory=inventory/

dependency:
  name: galaxy
  options:
    requirements-file: ${MOLECULE_SCENARIO_DIRECTORY}/requirements.yml

scenario:
  test_sequence:
    - dependency
    - destroy
    - create
    - converge
    - idempotence
    - verify
    - destroy
```

Declare the provider collection in `molecule/default/requirements.yml`:

```yaml
---
collections:
  - name: containers.podman
    version: ">=1.10.0"
```

Define the container as an Ansible inventory host in `molecule/default/inventory/hosts.yml`:

```yaml
---
all:
  children:
    molecule:
      hosts:
        molecule-fedora:
          ansible_connection: containers.podman.podman
          container_image: quay.io/centos/centos:stream9
          container_command: sleep 1d
          container_privileged: false
```

The inventory is the source of the container name, image, command, and connection details. The lifecycle playbooks read these values from `hostvars`.

## Create and destroy the test instance

`molecule/default/create.yml` creates the inventory defined container:

```yaml
---
- name: Create container instances
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Create containers from inventory
      containers.podman.podman_container:
        hostname: "{% raw %}{{ item }}{% endraw %}"
        name: "{% raw %}{{ item }}{% endraw %}"
        image: "{% raw %}{{ hostvars[item].container_image }}{% endraw %}"
        command: "{% raw %}{{ hostvars[item].container_command | default('sleep 1d') }}{% endraw %}"
        privileged: "{% raw %}{{ hostvars[item].container_privileged | default(false) }}{% endraw %}"
        state: started
      loop: "{% raw %}{{ groups['molecule'] }}{% endraw %}"

    - name: Wait for containers to be ready
      ansible.builtin.wait_for_connection:
        timeout: 30
      delegate_to: "{% raw %}{{ item }}{% endraw %}"
      loop: "{% raw %}{{ groups['molecule'] }}{% endraw %}"
```

`molecule/default/destroy.yml` removes the containers after the scenario:

```yaml
---
- name: Destroy container instances
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Remove containers
      containers.podman.podman_container:
        name: "{% raw %}{{ item }}{% endraw %}"
        state: absent
      loop: "{% raw %}{{ groups['molecule'] }}{% endraw %}"
```

For a more complete lifecycle implementation, see [Using podman containers](examples/podman.md).

## Converge the role

`molecule/default/converge.yml` applies the role under test to the inventory group:

```yaml
---
- name: Converge
  hosts: molecule
  gather_facts: false
  tasks:
    - name: Apply the role under test
      ansible.builtin.include_role:
        name: my_role
```

## Verify the result

`molecule/default/verify.yml` asserts the outcome of the role:

```yaml
---
- name: Verify
  hosts: molecule
  gather_facts: false
  tasks:
    - name: Read the role marker file
      ansible.builtin.stat:
        path: /tmp/molecule_role_marker
      register: marker

    - name: Confirm the role created the marker file
      ansible.builtin.assert:
        that:
          - marker.stat.exists
          - marker.stat.isreg
        fail_msg: The role marker file was not created
        success_msg: The role created the marker file
```

## Run the complete scenario

Run the full lifecycle from the role directory:

```bash
molecule test
```

Molecule runs the configured sequences:

```text
dependency → destroy → create → converge → idempotence → verify → destroy
```

The scenario should finish successfully and remove the test container. If it fails, rerun with `--debug` for more detail:

```bash
molecule --debug test
```

## Next steps

- Use [Using podman containers](examples/podman.md) for a detailed ansible-native Podman lifecycle.
- Use [Systemd Container](guides/systemd-container.md) when the role manages services and needs `systemd` as PID 1.
