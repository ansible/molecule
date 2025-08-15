# Workflow Reference

This document provides a comprehensive reference for Molecule's actions, sequences, and subcommands in the ansible-native approach.

## Overview

When running Molecule, you must provide a **subcommand** that determines what action or sequence of actions will be executed.

```bash
molecule <subcommand> [options]
```

Each subcommand executes either:
- **A single action** - Runs one specific playbook
- **A sequence** - Runs an ordered list of actions

### Execution Flow

**Subcommand** → **Sequence** → **Actions** → **Playbooks**

1. **Subcommands** are the commands to execute (e.g., `molecule test`, `molecule converge`)
2. **Sequences** are ordered lists of actions that can be customized in configuration
3. **Actions** correspond to individual playbooks containing tasks, roles, or other playbooks
4. **Playbooks** contain the actual Ansible tasks that perform the work

### Example Flow

```bash
molecule test
```

This executes the `test` sequence:
```
dependency → cleanup → destroy → syntax → create → prepare → converge → idempotence → side_effect → verify → cleanup → destroy
```

Each action runs its corresponding playbook:
- `create` → `create.yml` (tasks to provision testing resources)
- `converge` → `converge.yml` (tasks to apply configuration under test)  
- `verify` → `verify.yml` (tasks to validate results)
- etc.

### Customization

Sequences can be customized in the configuration:

```yaml
scenario:
  test_sequence:
    - create
    - converge
    - verify
    - destroy
```

This provides complete control over what actions run and in what order for any given subcommand.

## Actions

Actions are individual playbooks that perform specific testing lifecycle tasks. Each action has a distinct purpose and can be executed independently or as part of a sequence.

### Create

**Purpose**: Provision and initialize testing resources.

```yaml
# create.yml
---
- name: Create testing resources
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Create container network
      containers.podman.podman_network:
        name: molecule-test-network
        state: present

    - name: Launch test containers
      containers.podman.podman_container:
        name: "{% raw %}{{ item }}{% endraw %}"
        image: "{% raw %}{{ hostvars[item].image }}{% endraw %}"
        state: started
        networks:
          - molecule-test-network
      loop: "{% raw %}{{ groups['test_resources'] }}{% endraw %}"

    - name: Wait for resource readiness
      ansible.builtin.wait_for:
        port: "{% raw %}{{ hostvars[item].port }}{% endraw %}"
        host: "{% raw %}{{ hostvars[item].ansible_host }}{% endraw %}"
        timeout: 30
      loop: "{% raw %}{{ groups['test_resources'] }}{% endraw %}"
```

### Prepare

**Purpose**: Configure testing resources and install dependencies before testing.

```yaml
# prepare.yml
---
- name: Prepare testing environment
  hosts: test_resources
  tasks:
    - name: Update package cache
      ansible.builtin.package:
        update_cache: true

    - name: Install testing dependencies
      ansible.builtin.package:
        name:
          - python3-pip
          - curl
          - jq
        state: present

    - name: Create test directories
      ansible.builtin.file:
        path: /opt/test-data
        state: directory
        mode: '0755'

    - name: Copy test configuration files
      ansible.builtin.copy:
        src: "{% raw %}{{ item }}{% endraw %}"
        dest: /etc/test-config/
      with_fileglob:
        - "files/test-configs/*"
```

### Converge

**Purpose**: Apply the configuration or code being tested.

```yaml
# converge.yml
---
- name: Execute primary testing target
  hosts: test_resources
  tasks:
    - name: Apply collection role under test
      ansible.builtin.include_role:
        name: my_namespace.my_collection.target_role
      vars:
        role_environment: testing
        enable_debug_mode: true

    - name: Deploy application configuration
      ansible.builtin.template:
        src: app.conf.j2
        dest: /etc/myapp/app.conf
        mode: '0644'
      notify: restart application service

    - name: Ensure services are running
      ansible.builtin.systemd:
        name: "{% raw %}{{ item }}{% endraw %}"
        state: started
        enabled: true
      loop:
        - myapp
        - monitoring-agent

  handlers:
    - name: restart application service
      ansible.builtin.systemd:
        name: myapp
        state: restarted
```

### Verify

**Purpose**: Test that the applied configuration works as expected.

```yaml
# verify.yml
---
- name: Verify application functionality
  hosts: test_resources
  tasks:
    - name: Check service health endpoints
      ansible.builtin.uri:
        url: "http://{% raw %}{{ ansible_host }}{% endraw %}:8080/health"
        method: GET
        status_code: 200
        return_content: true
      register: health_check

    - name: Verify configuration files exist
      ansible.builtin.stat:
        path: /etc/myapp/app.conf
      register: config_file

    - name: Assert configuration is correct
      ansible.builtin.assert:
        that:
          - config_file.stat.exists
          - health_check.json.status == "healthy"
          - health_check.json.version is defined

    - name: Test inter-service communication
      ansible.builtin.command:
        cmd: curl -s http://localhost:8080/api/status
      register: api_response
      changed_when: false

    - name: Validate API response format
      ansible.builtin.assert:
        that:
          - api_response.stdout | from_json | json_query('services[*].status') | unique == ['running']
```

### Idempotence

**Purpose**: Verify that running converge twice produces no changes (idempotency test).

```yaml
# Note: Idempotence typically re-runs the converge playbook
# No separate playbook needed - Molecule handles this automatically
# The test passes if the second converge run reports zero changes
```

### Side Effect

**Purpose**: Test interactions with external systems or simulate failure conditions.

```yaml
# side_effect.yml
---
- name: Simulate external system interactions
  hosts: test_resources
  tasks:
    - name: Simulate network partition
      ansible.builtin.iptables:
        chain: OUTPUT
        destination: "{% raw %}{{ external_service_ip }}{% endraw %}"
        jump: DROP
        state: present

    - name: Test graceful degradation
      ansible.builtin.uri:
        url: "http://{% raw %}{{ ansible_host }}{% endraw %}:8080/health"
        method: GET
        status_code: [200, 503]

    - name: Restore network connectivity
      ansible.builtin.iptables:
        chain: OUTPUT
        destination: "{% raw %}{{ external_service_ip }}{% endraw %}"
        jump: DROP
        state: absent

    - name: Verify service recovery
      ansible.builtin.uri:
        url: "http://{% raw %}{{ ansible_host }}{% endraw %}:8080/health"
        method: GET
        status_code: 200
        retries: 5
        delay: 2
```

### Cleanup

**Purpose**: Remove temporary files and reset testing resources to clean state.

```yaml
# cleanup.yml
---
- name: Clean up testing artifacts
  hosts: test_resources
  tasks:
    - name: Stop test services
      ansible.builtin.systemd:
        name: "{% raw %}{{ item }}{% endraw %}"
        state: stopped
      loop:
        - test-daemon
        - mock-service
      ignore_errors: true

    - name: Remove temporary test files
      ansible.builtin.file:
        path: "{% raw %}{{ item }}{% endraw %}"
        state: absent
      loop:
        - /tmp/test-data
        - /opt/test-logs
        - /var/cache/test-artifacts

    - name: Reset configuration to defaults
      ansible.builtin.copy:
        src: default.conf
        dest: /etc/myapp/app.conf
        backup: true

    - name: Clear test databases
      ansible.builtin.command:
        cmd: psql -c "DROP DATABASE IF EXISTS test_db;"
      become_user: postgres
      ignore_errors: true
```

### Destroy

**Purpose**: Remove all testing resources and clean up infrastructure.

```yaml
# destroy.yml
---
- name: Destroy testing resources
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Stop and remove test containers
      containers.podman.podman_container:
        name: "{% raw %}{{ item }}{% endraw %}"
        state: absent
        force: true
      loop: "{% raw %}{{ groups['test_resources'] }}{% endraw %}"
      ignore_errors: true

    - name: Remove container networks
      containers.podman.podman_network:
        name: molecule-test-network
        state: absent

    - name: Clean up cloud resources
      amazon.aws.ec2_instance:
        instance_ids: "{% raw %}{{ hostvars[item].instance_id }}{% endraw %}"
        state: absent
        wait: true
      loop: "{% raw %}{{ groups['cloud_resources'] | default([]) }}{% endraw %}"
      when: cloud_cleanup_enabled | default(false)

    - name: Remove temporary directories
      ansible.builtin.file:
        path: "{% raw %}{{ molecule_ephemeral_directory }}{% endraw %}"
        state: absent
```

## Sequences

Sequences define the order and combination of actions to execute for different testing workflows.

## Sequences Without Shared State

In non-shared state mode (default), each scenario manages its own complete lifecycle.

### Default Test Sequence

The standard comprehensive testing sequence:

```yaml
scenario:
  test_sequence:
    - create
    - prepare
    - converge
    - verify
    - idempotence
    - verify
    - cleanup
    - destroy
```

### Component Test Sequence

For testing individual components without full lifecycle:

```yaml
scenario:
  test_sequence:
    - prepare
    - converge
    - verify
    - idempotence
    - verify
    - cleanup
```

### Development Sequence

Quick iteration cycle for development:

```yaml
scenario:
  test_sequence:
    - converge
    - verify
```

### Integration Test Sequence

For testing with external dependencies:

```yaml
scenario:
  test_sequence:
    - create
    - prepare
    - side_effect
    - converge
    - verify
    - cleanup
    - destroy
```

## Sequences With Shared State

With `shared_state: true`, the default scenario manages infrastructure while component scenarios focus on testing.

### Lifecycle Management Sequence (Default Scenario)

```yaml
# scenarios/default/molecule.yml
---
scenario:
  test_sequence:
    - create
    - destroy
```

### Component Testing Sequences

```yaml
# scenarios/role1/molecule.yml
---
scenario:
  test_sequence:
    - converge
    - verify

# scenarios/role2/molecule.yml  
---
scenario:
  test_sequence:
    - prepare
    - converge
    - verify
    - idempotence

# scenarios/integration/molecule.yml
---
scenario:
  test_sequence:
    - side_effect
    - converge
    - verify
```

### Sequence Inheritance

#### Global Configuration (config.yml)

```yaml
---
ansible:
  executor:
    args:
      ansible_playbook:
        - --inventory=inventory/

scenario:
  test_sequence:
    - create
    - prepare
    - converge
    - verify
    - destroy

shared_state: true
```

#### Scenario-Specific Override (scenarios/unit/molecule.yml)

```yaml
---
scenario:
  test_sequence:
    - converge
    - verify
    - idempotence
    - verify

# Inherits ansible config and shared_state from config.yml
```

#### Complete Scenario Override (scenarios/integration/molecule.yml)

```yaml
---
ansible:
  env:
    INTEGRATION_MODE: true
    
scenario:
  test_sequence:
    - create
    - prepare
    - side_effect
    - converge
    - verify
    - cleanup
    - destroy

shared_state: false  # Override global setting
```

### Shared State Sequences

#### Default Scenario (Lifecycle Manager)

```yaml
# scenarios/default/molecule.yml
---
scenario:
  test_sequence:
    - create
    - destroy
```

#### Component Scenarios

```yaml
# scenarios/role1/molecule.yml
---
scenario:
  test_sequence:
    - converge
    - verify

# scenarios/role2/molecule.yml  
---
scenario:
  test_sequence:
    - prepare
    - converge
    - verify
    - idempotence

# scenarios/role3/molecule.yml
---
scenario:
  test_sequence:
    - side_effect
    - converge
    - verify
```

## Subcommands

Molecule subcommands map to either complete sequences or individual actions.

### Sequence Commands

These commands execute complete sequences of actions:

#### `molecule test`
- **Purpose**: Execute the full test sequence
- **Sequence**: `dependency`, `cleanup`, `destroy`, `syntax`, `create`, `prepare`, `converge`, `idempotence`, `side_effect`, `verify`, `cleanup`, `destroy`
- **Usage**: `molecule test [scenario-name]`
- **Behavior**: 
  - Always starts fresh (destroys existing resources)
  - Runs all actions in sequence order
  - Stops on first failure unless `--destroy=never`

#### `molecule check`
- **Purpose**: Perform a dry-run of the provisioning sequence
- **Sequence**: `dependency`, `cleanup`, `destroy`, `syntax`, `create`, `prepare`, `converge`
- **Usage**: `molecule check [scenario-name]`
- **Behavior**: Validates configuration without permanent changes

#### `molecule converge`
- **Purpose**: Execute the convergence sequence
- **Sequence**: `dependency`, `create`, `prepare`, `converge`
- **Usage**: `molecule converge [scenario-name]`
- **Behavior**: Ensures resources exist and applies configuration

#### `molecule create`
- **Purpose**: Execute the creation sequence
- **Sequence**: `dependency`, `create`, `prepare`
- **Usage**: `molecule create [scenario-name]`
- **Behavior**: Sets up testing resources and prepares them

#### `molecule destroy`
- **Purpose**: Execute the destruction sequence
- **Sequence**: `dependency`, `cleanup`, `destroy`
- **Usage**: `molecule destroy [scenario-name]`
- **Behavior**: Cleans up and removes all testing resources

### Direct Action Commands

These commands execute single actions only:

#### `molecule prepare`
- **Action**: `prepare`
- **Purpose**: Configure existing resources for testing
- **Usage**: `molecule prepare [scenario-name]`
- **Behavior**: Runs prepare playbook only, resources must already exist

#### `molecule verify`
- **Action**: `verify`
- **Purpose**: Run verification tests only
- **Usage**: `molecule verify [scenario-name]`
- **Behavior**: Tests current state without changes

#### `molecule idempotence`
- **Action**: `idempotence`
- **Purpose**: Test idempotency by running converge twice
- **Usage**: `molecule idempotence [scenario-name]`
- **Behavior**: Runs converge, then converge again, expects no changes

#### `molecule side-effect`
- **Action**: `side_effect`
- **Purpose**: Execute side effect testing
- **Usage**: `molecule side-effect [scenario-name]`
- **Behavior**: Runs side_effect playbook only

#### `molecule cleanup`
- **Action**: `cleanup`
- **Purpose**: Clean up test artifacts without destroying resources
- **Usage**: `molecule cleanup [scenario-name]`
- **Behavior**: Runs cleanup playbook only

#### `molecule syntax`
- **Action**: `syntax`
- **Purpose**: Check playbook syntax
- **Usage**: `molecule syntax [scenario-name]`
- **Behavior**: Validates Ansible syntax without execution

#### `molecule dependency`
- **Action**: `dependency`
- **Purpose**: Install role dependencies
- **Usage**: `molecule dependency [scenario-name]`
- **Behavior**: Downloads and installs required dependencies only

### Utility Commands

These commands provide information and access:

#### `molecule list`
- **Purpose**: Display scenario information and status
- **Usage**: `molecule list [scenario-name]`
- **Behavior**: Shows current state of instances

#### `molecule login`
- **Purpose**: Log into a running instance
- **Usage**: `molecule login [--host hostname] [scenario-name]`
- **Behavior**: Opens shell session to instance

#### `molecule matrix`
- **Purpose**: Display test matrix for scenarios
- **Usage**: `molecule matrix [subcommand] [scenario-name]`
- **Behavior**: Shows sequence of actions for given subcommand

### Command Groups

#### Development Workflow
```bash
# Quick iteration cycle
molecule create
molecule converge
molecule verify

# Make changes, then repeat
molecule converge
molecule verify

# Clean up when done
molecule destroy
```

#### Full Testing Workflow
```bash
# Complete test suite
molecule test

# Or step by step
molecule create
molecule prepare  
molecule converge
molecule verify
molecule idempotence
molecule verify
molecule cleanup
molecule destroy
```

#### Debugging Workflow
```bash
# Create and access resources
molecule create
molecule prepare

# Debug interactively
molecule login

# Test changes
molecule converge
molecule verify

# Leave resources for investigation
# (skip destroy)
```

#### Multi-Scenario Testing
```bash
# Test specific scenarios
molecule test --scenario unit
molecule test --scenario integration
molecule test --scenario performance

# Test all scenarios
molecule test --all
```

### Command Behavior with Shared State

#### With `shared_state: true`

```bash
# Default scenario manages lifecycle
molecule create --scenario default

# Component scenarios use existing resources
molecule converge --scenario role1
molecule verify --scenario role1

molecule converge --scenario role2  
molecule verify --scenario role2

# Default scenario cleans up
molecule destroy --scenario default
```

#### Without `shared_state` (default)

```bash
# Each scenario manages its own resources
molecule test --scenario role1  # Creates, tests, destroys
molecule test --scenario role2  # Creates, tests, destroys  
molecule test --scenario role3  # Creates, tests, destroys
```

### Advanced Command Usage

#### Selective Testing
```bash
# Skip destroy for debugging
molecule test --destroy=never

# Test with specific verbosity
molecule test -v
molecule converge -vvv

# Force recreation
molecule destroy
molecule test
```

#### Parallel Execution
```bash
# Test multiple scenarios in parallel
molecule test --scenario unit &
molecule test --scenario integration &
wait
```

#### Environment-Specific Testing
```bash
# Test with environment variables
MOLECULE_DOCKER_HOST=tcp://remote:2376 molecule test
TEST_DATABASE_URL=postgresql://test-db molecule verify
```

This comprehensive reference covers all aspects of Molecule's action and sequence system, providing both the conceptual understanding and practical examples needed for effective ansible-native testing workflows.
