# Playbook Testing

This guide demonstrates testing Ansible playbooks using Molecule within an ansible-creator playbook project. It covers the fundamentals of playbook testing, container and network device testing scenarios, and complete test lifecycle management.

## Prerequisites

Before starting, ensure you have the following installed:

- [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html) (ansible-core)
- [Molecule](https://molecule.readthedocs.io/en/latest/installation/)
- [ansible-creator](https://ansible.readthedocs.io/projects/creator/) for scaffolding
- [Podman](https://podman.io/getting-started/installation) for container testing

```bash
# Install ansible-creator in your virtual environment
pip install ansible-creator
```

## Creating a Playbook Project

**Initialize a playbook project using ansible-creator:**

   ```bash
   ansible-creator init playbook-project --init-path /tmp/my-playbooks
   cd /tmp/my-playbooks
   ```

   This creates the following structure:

   ```
   my-playbooks/
   ├── ansible.cfg
   ├── ansible-navigator.yml
   ├── collections/
   │   └── requirements.yml
   ├── inventory/
   │   ├── group_vars/
   │   ├── host_vars/
   │   └── hosts.yml
   ├── linux_playbook.yml
   ├── network_playbook.yml
   └── site.yml
   ```

**Create Molecule requirements file:**

   ```bash
   mkdir molecule
   cat > molecule/requirements.yml << 'EOF'
   ---
   collections:
     - name: containers.podman
       version: ">=1.10.0"
     - name: arista.eos
       version: ">=6.0.0"
   EOF
   ```

**Initialize Molecule scenarios for different testing needs:**

   ```bash
   # Linux container testing scenario
   molecule init scenario linux

   # Network device testing scenario
   molecule init scenario network
   ```

## Linux Container Testing Scenario

This scenario tests playbooks against Linux containers using Podman.

### Configure the Linux Scenario

**Update `molecule/linux/molecule.yml`:**

The `molecule.yml` file is the scenario-specific configuration that tailors Molecule's behavior to the needs of this testing scenario.

```yaml
---
dependency:
  name: galaxy
  options:
    requirements-file: ../requirements.yml

ansible:
  cfg:
    defaults:
      collections_path: collections
      inventory: inventory/hosts.yml

scenario:
  test_sequence:
    - dependency
    - create
    - prepare
    - converge
    - idempotence
    - verify
    - cleanup
    - destroy
```

**Create `molecule/linux/inventory.yml`:**

The inventory defines the testing resources and their configuration details that Molecule will use to create and manage test instances.

```yaml
---
all:
  children:
    webservers:
      hosts:
        web-server:
          ansible_host: web-server
          container_image: quay.io/centos/centos:stream9
          container_command: /sbin/init
          container_privileged: true
      vars:
        http_port: 80
        server_name: test-web
        required_packages:
          - python3
          - systemd
    databases:
      hosts:
        db-server:
          ansible_host: db-server
          container_image: quay.io/centos/centos:stream9
          container_command: /sbin/init
          container_privileged: true
      vars:
        db_name: testdb
        db_user: testuser
        required_packages:
          - python3
          - systemd
```

**Create `molecule/linux/create.yml`:**

The create playbook is used to instantiate the testing resources defined in the inventory, provisioning containers and establishing connectivity.

```yaml
---
- name: Create container instances
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Create container network
      containers.podman.podman_network:
        name: molecule-linux-test
        state: present

    - name: Create test containers
      containers.podman.podman_container:
        name: "{% raw %}{{ hostvars[item].ansible_host }}{% endraw %}"
        image: "{% raw %}{{ hostvars[item].container_image }}{% endraw %}"
        command: "{% raw %}{{ hostvars[item].container_command }}{% endraw %}"
        privileged: "{% raw %}{{ hostvars[item].container_privileged }}{% endraw %}"
        state: started
        networks:
          - molecule-linux-test
        systemd: true
      loop: "{% raw %}{{ groups['all'] }}{% endraw %}"

    - name: Wait for containers to be ready
      ansible.builtin.wait_for_connection:
        timeout: 300
      delegate_to: "{% raw %}{{ hostvars[item].ansible_host }}{% endraw %}"
      loop: "{% raw %}{{ groups['all'] }}{% endraw %}"
```

**Create `molecule/linux/prepare.yml`:**

The prepare playbook configures the testing resources with any prerequisites needed before running the main playbook under test.

```yaml
---
- name: Prepare container instances
  hosts: all
  gather_facts: false
  become: true
  tasks:
    - name: Install required packages
      ansible.builtin.dnf:
        name: "{% raw %}{{ required_packages }}{% endraw %}"
        state: present
      when: required_packages is defined
```

**Create `molecule/linux/converge.yml`:**

The converge playbook executes the main playbook being tested, applying your automation logic to the prepared testing resources.

```yaml
---
- name: Converge
  ansible.builtin.import_playbook: ../../linux_playbook.yml
```

**Create `molecule/linux/verify.yml`:**

The verify playbook validates that the converge playbook achieved the desired results by testing the final state of the resources.

```yaml
---
- name: Verify
  hosts: all
  gather_facts: true
  tasks:
    - name: Check required packages are installed
      ansible.builtin.package_facts:
        manager: auto

    - name: Verify python3 is installed
      ansible.builtin.assert:
        that:
          - "'python3' in ansible_facts.packages"
        fail_msg: "Python3 package not found"

    - name: Verify systemd service is running
      ansible.builtin.systemd:
        name: systemd-logind
        state: started
      check_mode: true
      register: systemd_check
      failed_when: false

    - name: Assert systemd is active
      ansible.builtin.assert:
        that:
          - systemd_check is not failed
        fail_msg: "Systemd service not running"
```

**Create `molecule/linux/cleanup.yml`:**

The cleanup playbook removes temporary artifacts and resets the testing resources to a clean state before destruction.

```yaml
---
- name: Cleanup
  hosts: all
  gather_facts: false
  tasks:
    - name: Remove test artifacts
      ansible.builtin.file:
        path: /tmp/molecule-test
        state: absent
      become: true
```

**Create `molecule/linux/destroy.yml`:**

The destroy playbook tears down all testing resources, removing containers and networks to return the system to its original state.

```yaml
---
- name: Destroy container instances
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Remove test containers
      containers.podman.podman_container:
        name: "{% raw %}{{ hostvars[item].ansible_host }}{% endraw %}"
        state: absent
      loop: "{% raw %}{{ groups['all'] }}{% endraw %}"
      failed_when: false

    - name: Remove container network
      containers.podman.podman_network:
        name: molecule-linux-test
        state: absent
      failed_when: false
```

## Network Device Testing Scenario

This scenario tests playbooks against Arista EOS network devices using containerized cEOS.

### Configure the Network Scenario

**Update `molecule/network/molecule.yml`:**

This scenario-specific configuration adapts Molecule for network device testing with simplified sequences and network-specific settings.

```yaml
---
dependency:
  name: galaxy
  options:
    requirements-file: ../requirements.yml

ansible:
  cfg:
    defaults:
      collections_path: collections
      inventory: inventory/hosts.yml
      host_key_checking: false

scenario:
  name: network
  description: Test against network devices
  test_sequence:
    - dependency
    - create
    - converge
    - verify
    - cleanup
    - destroy
```

**Create `molecule/network/inventory.yml`:**

The network inventory defines containerized network devices with connection parameters and container configuration for realistic device testing.

```yaml
---
all:
  children:
    arista_switches:
      hosts:
        eos-switch-01:
          ansible_host: eos-switch-01
          ansible_network_os: eos
          ansible_user: admin
          ansible_password: admin
          ansible_connection: ansible.netcommon.network_cli
          container_image: ceos:latest
          container_privileged: true
          container_env:
            CEOS: 1
            EOS_PLATFORM: ceoslab
            container: docker
      vars:
        ansible_python_interpreter: "{% raw %}{{ ansible_playbook_python }}{% endraw %}"
```

**Create `molecule/network/create.yml`:**

The create playbook launches containerized network devices and waits for both SSH and API services to become available for testing.

```yaml
---
- name: Create network device containers
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Create container network
      containers.podman.podman_network:
        name: molecule-network-test
        state: present

    - name: Create EOS containers
      containers.podman.podman_container:
        name: "{% raw %}{{ hostvars[item].ansible_host }}{% endraw %}"
        image: "{% raw %}{{ hostvars[item].container_image }}{% endraw %}"
        privileged: "{% raw %}{{ hostvars[item].container_privileged }}{% endraw %}"
        state: started
        networks:
          - molecule-network-test
        ports:
          - "2200:22"
          - "2600:443"
        volumes:
          - /etc/sysctl.d/99-zceos.conf:/etc/sysctl.d/99-zceos.conf:ro
        tmpfs:
          - /tmp
        command: /sbin/init
        env: "{% raw %}{{ hostvars[item].container_env }}{% endraw %}"
        network_cli_ssh_type: paramiko
      loop: "{% raw %}{{ groups['arista_switches'] }}{% endraw %}"

    - name: Wait for SSH to be available
      ansible.builtin.wait_for:
        host: "{% raw %}{{ hostvars[item].ansible_host }}{% endraw %}"
        port: 22
        timeout: 300
      loop: "{% raw %}{{ groups['arista_switches'] }}{% endraw %}"

    - name: Wait for EOS API to be ready
      ansible.builtin.uri:
        url: "https://{% raw %}{{ hostvars[item].ansible_host }}{% endraw %}:443/command-api"
        method: GET
        validate_certs: false
        timeout: 10
      register: api_check
      until: api_check.status == 200
      retries: 30
      delay: 10
      loop: "{% raw %}{{ groups['arista_switches'] }}{% endraw %}"
      failed_when: false
```

**Create `molecule/network/converge.yml`:**

The converge playbook executes the network playbook under test against the containerized network devices.

```yaml
---
- name: Converge
  ansible.builtin.import_playbook: ../../network_playbook.yml
```

**Create `molecule/network/verify.yml`:**

The verify playbook tests network device functionality using EOS-specific commands to validate the playbook's effects on device configuration.

```yaml
---
- name: Verify network devices
  hosts: arista_switches
  gather_facts: false
  connection: ansible.netcommon.network_cli
  tasks:
    - name: Get EOS version
      arista.eos.eos_command:
        commands:
          - show version
      register: version_output

    - name: Verify EOS version contains expected info
      ansible.builtin.assert:
        that:
          - "'Arista' in version_output.stdout[0]"
        fail_msg: "EOS version check failed"

    - name: Gather EOS facts
      arista.eos.eos_facts:
        gather_subset: min
      register: eos_facts

    - name: Verify system facts
      ansible.builtin.assert:
        that:
          - eos_facts.ansible_facts.ansible_net_version is defined
          - eos_facts.ansible_facts.ansible_net_hostname is defined
        fail_msg: "Required EOS facts not available"
```

**Create `molecule/network/cleanup.yml`:**

The cleanup playbook removes any test configurations from the network devices to restore them to a clean state.

```yaml
---
- name: Cleanup network configuration
  hosts: arista_switches
  gather_facts: false
  connection: ansible.netcommon.network_cli
  tasks:
    - name: Remove test configurations
      arista.eos.eos_config:
        lines:
          - no interface Loopback99
        backup: false
      failed_when: false
```

**Create `molecule/network/destroy.yml`:**

The destroy playbook removes the containerized network devices and networks, completing the test lifecycle cleanup.

```yaml
---
- name: Destroy network device containers
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Remove EOS containers
      containers.podman.podman_container:
        name: "{% raw %}{{ hostvars[item].ansible_host }}{% endraw %}"
        state: absent
      loop: "{% raw %}{{ groups['arista_switches'] }}{% endraw %}"
      failed_when: false

    - name: Remove container network
      containers.podman.podman_network:
        name: molecule-network-test
        state: absent
      failed_when: false
```

## Running the Tests

### Testing Individual Scenarios

**Linux Scenario:**

```bash
# Test the complete lifecycle
molecule test --scenario-name linux --report --command-borders

# Run specific actions
molecule create --scenario-name linux --report --command-borders
molecule converge --scenario-name linux --report --command-borders
molecule verify --scenario-name linux --report --command-borders
```

**Network Scenario:**

```bash
# Test the network scenario
molecule test --scenario-name network --report --command-borders

# Converge only
molecule converge --scenario-name network --report --command-borders
```

### Expected Output

```bash
$ molecule test --scenario-name linux --report --command-borders

INFO     linux ➜ discovery: scenario test matrix: dependency, create, prepare, converge, idempotence, verify, cleanup, destroy
INFO     linux ➜ dependency: Executing
INFO     linux ➜ create: Executing
  ┌──────────────────────────────────────────────────────────────────────────────────
  │ ansible-playbook --inventory /tmp/molecule/linux/inventory
  │   --skip-tags molecule-notest,notest
  │   /tmp/molecule/linux/create.yml
  │
  │
  │ PLAY [Create container instances] ********************************************
  │
  │ TASK [Create container network] **********************************************
  │ changed: [localhost]
  │
  │ TASK [Create test containers] ************************************************
  │ changed: [localhost] => (item=web-server)
  │ changed: [localhost] => (item=db-server)
  │
  │ TASK [Wait for containers to be ready] **************************************
  │ ok: [web-server]
  │ ok: [db-server]
  │
  │ PLAY RECAP ********************************************************************
  │ localhost                  : ok=2    changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
  │
  └─ Return code: 0 ─────────────────────────────────────────────────────────────────
INFO     linux ➜ create: Executed: Successful
INFO     linux ➜ prepare: Executing
  ┌──────────────────────────────────────────────────────────────────────────────────
  │ ansible-playbook --inventory /tmp/molecule/linux/inventory
  │   --skip-tags molecule-notest,notest
  │   /tmp/molecule/linux/prepare.yml
  │
  │
  │ PLAY [Prepare container instances] *******************************************
  │
  │ TASK [Install required packages] *********************************************
  │ changed: [web-server] => (item=python3)
  │ changed: [db-server] => (item=python3)
  │ changed: [web-server] => (item=systemd)
  │ changed: [db-server] => (item=systemd)
  │
  │ PLAY RECAP ********************************************************************
  │ web-server                 : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
  │ db-server                  : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
  │
  └─ Return code: 0 ─────────────────────────────────────────────────────────────────
INFO     linux ➜ prepare: Executed: Successful
INFO     linux ➜ converge: Executing
INFO     linux ➜ idempotence: Executing
INFO     linux ➜ verify: Executing
INFO     linux ➜ cleanup: Executing
INFO     linux ➜ destroy: Executing

SCENARIO RECAP
linux                       : actions=8  successful=8  disabled=0  skipped=0  missing=0  failed=0
```

## Advanced Testing Patterns

### Environment-Specific Testing

Test playbooks with different inventory configurations:

```bash
# Test with specific inventory
molecule converge --scenario-name linux --inventory inventory/production.yml --report --command-borders
```

### Multiple Playbook Testing

Create scenarios to test different playbook combinations:

```bash
# Initialize scenario for site.yml testing
molecule init scenario site-testing

# Test the complete site playbook
molecule test --scenario-name site-testing --report --command-borders
```

### Parallel Testing

Run multiple scenarios simultaneously:

```bash
# Test both scenarios in parallel
molecule test --parallel --report --command-borders
```

## Summary

This guide demonstrated comprehensive playbook testing using Molecule with both container and network device scenarios. Key benefits include:

- **Complete test lifecycle management** with create, converge, verify, and cleanup phases
- **Multiple testing environments** supporting both Linux containers and network devices
- **Realistic testing scenarios** using actual device containers (cEOS) rather than simulation
- **Integration with ansible-creator** for standardized project structure
- **Flexible inventory management** supporting both static and dynamic configurations

The ansible-native approach ensures that your Molecule tests integrate seamlessly with existing Ansible workflows while providing comprehensive validation of playbook functionality across diverse infrastructure environments.
