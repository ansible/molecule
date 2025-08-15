# Getting Started with Playbook Testing

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

1. **Initialize a playbook project using ansible-creator:**

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

2. **Create Molecule requirements file:**

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

3. **Initialize Molecule scenarios for different testing needs:**

    ```bash
    # Linux container testing scenario
    molecule init scenario linux
    
    # Network device testing scenario  
    molecule init scenario network
    ```

## Linux Container Testing Scenario

This scenario tests playbooks against Linux containers using Podman.

### Configure the Linux Scenario

1. **Update `molecule/linux/molecule.yml`:**

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

2. **Create `molecule/linux/inventory.yml`:**

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

3. **Create `molecule/linux/create.yml`:**

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

4. **Create `molecule/linux/prepare.yml`:**

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

5. **Create `molecule/linux/converge.yml`:**

    ```yaml
    ---
    - name: Converge
      ansible.builtin.import_playbook: ../../linux_playbook.yml
    ```

6. **Create `molecule/linux/verify.yml`:**

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

7. **Create `molecule/linux/cleanup.yml`:**

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

8. **Create `molecule/linux/destroy.yml`:**

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

1. **Update `molecule/network/molecule.yml`:**

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

2. **Create `molecule/network/inventory.yml`:**

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

3. **Create `molecule/network/create.yml`:**

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

4. **Create `molecule/network/converge.yml`:**

    ```yaml
    ---
    - name: Converge
      ansible.builtin.import_playbook: ../../network_playbook.yml
    ```

5. **Create `molecule/network/verify.yml`:**

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

6. **Create `molecule/network/cleanup.yml`:**

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

7. **Create `molecule/network/destroy.yml`:**

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

INFO     Running linux > dependency
═══════════════════════════════════════════
Running ansible-galaxy collection install -r requirements.yml

DETAILS
✓ 2 collections installed

INFO     Running linux > create
════════════════════════════════════
Running ansible-playbook create.yml

DETAILS
✓ Container network created
✓ 2 containers started
✓ Connection established to all hosts

INFO     Running linux > prepare  
═════════════════════════════════
Running ansible-playbook prepare.yml

DETAILS  
✓ Required packages installed

INFO     Running linux > converge
═══════════════════════════════════
Running ansible-playbook converge.yml

DETAILS
✓ linux_playbook.yml executed successfully

INFO     Running linux > idempotence
═════════════════════════════════════
Running ansible-playbook converge.yml

DETAILS
✓ Playbook is idempotent

INFO     Running linux > verify
════════════════════════════════
Running ansible-playbook verify.yml

DETAILS
✓ All verification checks passed

INFO     Running linux > cleanup
═════════════════════════════════
Running ansible-playbook cleanup.yml

DETAILS
✓ Test artifacts removed

INFO     Running linux > destroy
═════════════════════════════════
Running ansible-playbook destroy.yml

DETAILS
✓ All containers removed
✓ Networks cleaned up

SCENARIO RECAP
✓ linux: 7 actions completed successfully
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
