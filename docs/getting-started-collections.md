# Collection Testing

This guide demonstrates how to use Molecule to test Ansible collections with multiple components and shared testing resources. This approach builds a complete testing framework that showcases best practices for collection-level testing.

## Overview

This guide covers:

- An Ansible collection with multiple components (roles, plugins, filters, modules)
- Shared Molecule configuration across all scenarios
- 1:1 mapping of scenarios to collection components
- Collection plugin and content testing
- Testing resource management scenario (create/destroy)
- Component-specific testing scenarios (prepare/converge/verify/idempotence/cleanup)
- Shared state management for efficient testing

## Prerequisites

- ansible-creator installed
- Basic familiarity with Ansible and collections

## Creating the Collection Structure

Start by creating a new collection using ansible-creator:

```bash
ansible-creator init collection test_namespace.test_collection
cd test_namespace.test_collection
```

This creates the standard collection structure. Customize the Molecule testing setup by removing the default scaffold and creating the required structure:

```bash
# Remove default role scaffold (not needed for this example)
rm -rf roles/run

# Clear out default molecule setup
rm -rf extensions/molecule/*

# Create our custom structure
mkdir -p extensions/molecule/default/
```

Next, add some collection components to test. In this example, add roles:

```bash
ansible-creator add resource role role1
ansible-creator add resource role role2
ansible-creator add resource role role3
```

Note: This same pattern works for testing other collection components like plugins, modules, or filters by creating appropriate test scenarios for each component type.

## Shared Molecule Configuration

Molecule supports configuration inheritance through a base `config.yml` file that all scenarios can inherit from. This allows defining common settings once and overriding them per scenario as needed.

### Shared Inventory

The inventory defines the test targets and their configuration. Molecule leverages Ansible's native inventory system, supporting all Ansible inventory patterns:

- Single inventory files (YAML or INI format)
- Inventory directories with multiple files
- Dynamic inventory scripts
- Inventory plugins (cloud providers, CMDB systems)
- Mix of static and dynamic sources

The inventory should include all the details needed to initialize, instantiate, prepare, and access a testing resource.

Inventory can be specified through multiple methods:

- **Ansible executor arguments** (shown in config.yml examples)
- **ansible.cfg configuration** (`inventory = path/to/inventory`)
- **Environment variables** (`ANSIBLE_INVENTORY=path/to/inventory`)

Create `extensions/molecule/inventory.yml`:

```yaml
---
all:
  vars:
    tmp_dir: "{% raw %}{{ lookup('env', 'TMPDIR') | default('/tmp') }}{% endraw %}"
  children:
    test_resources:
      hosts:
        host_1:
          my_variable: 1_tsoh
          attributes:
            color: red
            size: small
            shape: square
          prerequisites:
            - A
            - B
            - C
        host_2:
          my_variable: 2_tsoh
          attributes:
            color: blue
            size: medium
            shape: rectangle
          prerequisites:
            - D
            - E
            - F
        host_3:
          my_variable: 3_tsoh
          attributes:
            color: green
            size: large
            shape: circle
          prerequisites:
            - G
            - H
            - I
      vars:
        ansible_connection: local
```

This inventory defines:

- Three test hosts with different characteristics
- Prerequisites lists for demonstrating preparation steps
- Local connection for testing without external infrastructure
- Attribute data for testing collection functionality

### Base Configuration (config.yml)

Create `extensions/molecule/config.yml`:

```yaml
---
ansible:
  executor:
    args:
      ansible_playbook:
        - {% raw %}--inventory=${MOLECULE_SCENARIO_DIRECTORY}/../inventory.yml{% endraw %}

scenario:
  test_sequence:
    - prepare
    - converge
    - verify
    - idempotence
    - verify
    - cleanup

shared_state: true
```

This configuration:

- Points all scenarios to the shared inventory file
- Defines the default test sequence for testing
- Enables shared state which delegates all `create` and `destroy` actions to the `default` scenario
- Will be inherited by all scenario-specific molecule.yml files

### Alternative Inventory Sources

Molecule's Ansible-native design supports various inventory patterns. Here's an example using an inventory directory structure:

```bash
# Create inventory directory with multiple sources
mkdir -p extensions/molecule/inventory
```

**inventory/hosts.yml** - Static host definitions:

```yaml
---
all:
  children:
    test_resources:
      hosts:
        app-server-01:
          ansible_host: 192.168.1.10
          component_type: application
        app-server-02:
          ansible_host: 192.168.1.11
          component_type: application
        db-server-01:
          ansible_host: 192.168.1.20
          component_type: database
      vars:
        ansible_connection: ssh
        ansible_user: testuser
```

**inventory/group_vars/all.yml** - Global variables:

```yaml
---
test_environment: lab
deployment_timestamp: "{% raw %}{{ ansible_date_time.epoch }}{% endraw %}"
```

**inventory/group_vars/test_resources.yml** - Group-specific variables:

```yaml
---
monitoring_enabled: true
backup_schedule: "0 2 * * *"
```

**config.yml** updated to use inventory directory:

```yaml
---
ansible:
  executor:
    args:
      ansible_playbook:
        - {% raw %}--inventory=${MOLECULE_SCENARIO_DIRECTORY}/../inventory/{% endraw %}

scenario:
  test_sequence:
    - prepare
    - converge
    - verify
    - idempotence
    - verify
    - cleanup

shared_state: true
```

This demonstrates Molecule's native integration with Ansible's inventory system, allowing teams to use familiar inventory patterns and structures for testing.

## Configuration Inheritance

Molecule uses a hierarchical configuration system where scenario-specific `molecule.yml` files override or extend the base `config.yml`:

1. **Base config.yml**: Shared settings for all scenarios
2. **Scenario molecule.yml**: Scenario-specific overrides and extensions

### Default Scenario Configuration

In this example, the default scenario has a different purpose - testing resource management rather than component testing. Create `extensions/molecule/default/molecule.yml`:

```yaml
---
scenario:
  test_sequence:
    - create
    - destroy
```

This **overrides** the base configuration's test_sequence, changing it from the full component testing lifecycle to just testing resource management.

### Component Scenario Configuration

For component scenarios, create empty `molecule.yml` files that inherit everything from `config.yml`:

```bash
mkdir -p extensions/molecule/role1/
touch extensions/molecule/role1/molecule.yml

mkdir -p extensions/molecule/role2/
touch extensions/molecule/role2/molecule.yml

mkdir -p extensions/molecule/role3/
touch extensions/molecule/role3/molecule.yml
```

Empty molecule.yml files inherit the complete configuration from `config.yml`, including the full test sequence.

## Scenario Playbooks

Each scenario requires specific playbooks based on its test sequence. Each type serves a specific purpose:

### Testing Resource Management Playbooks (Default Scenario)

The default scenario manages shared testing resources that component scenarios will use. These resources can be infrastructure (VMs, containers), applications (databases, web services), API endpoints, or any other testing dependencies.

**create.yml** - Testing resource initialization:

```yaml
---
- name: Initialize all resources
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Initializing resource
      ansible.builtin.copy:
        dest: "{% raw %}{{ tmp_dir }}{{ item }}_created.yml{% endraw %}"
        content: |
          {% raw %}{{ hostvars[item].attributes }}{% endraw %}
      loop: "{% raw %}{{ groups['test_resources'] }}{% endraw %}"

- name: Ensure resource creation
  hosts: test_resources
  gather_facts: false
  tasks:
    - name: Resource initialized
      ansible.builtin.stat:
        path: "{% raw %}{{ tmp_dir }}{{ inventory_hostname }}_created.yml{% endraw %}"
      register: result
      failed_when: not result.stat.exists
```

**destroy.yml** - Testing resource cleanup:

```yaml
---
- hosts: localhost
  gather_facts: false
  tasks:
    - name: Destroy the resources
      ansible.builtin.file:
        path: "{% raw %}{{ tmp_dir }}{{ item }}_created.yml{% endraw %}"
        state: absent
      loop: "{% raw %}{{ groups['test_resources'] }}{% endraw %}"
```

### Collection Testing Playbooks

Each scenario gets the same set of playbooks, each is a unique test.

**prepare.yml** - Component prerequisite satisfaction:

```yaml
---
- hosts: test_resources
  gather_facts: false
  tasks:
    - name: Prepare the resource
      ansible.builtin.debug:
        msg: "Satisfying prerequisite {% raw %}{{ item }}{% endraw %}"
      loop: "{% raw %}{{ prerequisites }}{% endraw %}"
```

**converge.yml** - Main test execution:

```yaml
---
- hosts: test_resources
  gather_facts: false
  tasks:
    - name: Touch a file in the temporary directory
      ansible.builtin.copy:
        dest: "{% raw %}{{ tmp_dir }}{{ inventory_hostname }}.txt{% endraw %}"
        content: Molecule is running on {% raw %}{{ inventory_hostname }}{% endraw %}
      vars:
        tmp_dir: "{% raw %}{{ ansible_env.TMPDIR | default('/tmp') }}/{% endraw %}"

    - name: Include the collection component
      include_role:
        name: test_namespace.test_collection.roleX
```

**verify.yml** - Validation:

```yaml
---
- hosts: test_resources
  gather_facts: false
  tasks:
    - name: Check if my_variable is set
      assert:
        that:
          - my_variable == inventory_hostname | reverse
        fail_msg: "my_variable is not set"
        success_msg: "my_variable is set"

    - name: Verify the functionality of a collection plugin
      ansible.builtin.set_fact:
        output: "{% raw %}{{ inventory_hostname | test_namespace.test_collection.sample_filter }}{% endraw %}"

    - name: Verify the output
      ansible.builtin.assert:
        that:
          - output == expected
        fail_msg: "Output '{% raw %}{{ output }}{% endraw %}' Expected '{% raw %}{{ expected }}{% endraw %}'"
      vars:
        expected: "Hello, {% raw %}{{ inventory_hostname }}{% endraw %}"
```

**cleanup.yml** - Test artifact removal:

```yaml
---
- hosts: test_resources
  gather_facts: false
  tasks:
    - name: Remove the temporary directory
      ansible.builtin.file:
        path: "{% raw %}{{ tmp_dir }}{{ inventory_hostname }}.txt{% endraw %}"
        state: absent
      vars:
        tmp_dir: "{% raw %}{{ ansible_env.TMPDIR | default('/tmp') }}/{% endraw %}"
```

## Understanding Scenario Types

### Default Scenario: Testing Resource Lifecycle Manager

- **Purpose**: Manage infrastructure lifecycle for ALL scenarios when `shared_state` is enabled
- **Test Sequence**: `create → destroy` (only these actions run)
- **When it runs**: `create` runs first, `destroy` runs last in `--all` mode
- **Playbooks**: create.yml, destroy.yml
- **Effect**: Creates/destroys resources that all component scenarios will use

### Component Scenarios: Collection Testing Only

- **Purpose**: Test individual collection components using shared infrastructure
- **Test Sequence**: `prepare → converge → verify → idempotence → verify → cleanup` (no create/destroy when `shared_state` is enabled)
- **When they run**: After infrastructure creation, before infrastructure destruction
- **Playbooks**: prepare.yml, converge.yml, verify.yml, cleanup.yml (create.yml and destroy.yml are skipped)
- **Effect**: Test collection components against the infrastructure created by the default scenario

## Shared State vs Per-Scenario Resources

Molecule offers two resource management approaches:

### Shared State (Required for This Configuration)

Shared state can be enabled in two ways:

#### 1. Configuration File (Recommended)

Add `shared_state: true` to your base `config.yml` or scenario-specific `molecule.yml`:

```yaml
---
ansible:
  executor:
    args:
      ansible_playbook:
        - --inventory=${MOLECULE_SCENARIO_DIRECTORY}/../inventory.yml

scenario:
  test_sequence:
    - prepare
    - converge
    - verify
    - idempotence
    - verify
    - cleanup

shared_state: true
```

When `shared_state: true` is set in the configuration, scenarios automatically share state without requiring command-line flags. This can be configured per-scenario or in a shared configuration.

#### 2. Command Line (Per-Execution)

```bash
molecule test --all --shared-state
```

**How shared state works:**

With `shared_state` enabled, the **default scenario becomes the lifecycle manager** for all scenarios:

- **Default scenario handles create/destroy**: The default scenario's `create` and `destroy` actions manage the infrastructure lifecycle for ALL scenarios
- **Component scenarios skip create/destroy**: Individual scenarios (role1, role2, role3) only run their test sequence (prepare, converge, verify, etc.) - they do not create or destroy their own resources
- **Shared ephemeral state**: All scenarios share the same state directory, allowing them to access resources created by the default scenario

**Why this approach is required for this configuration:**

- The default scenario creates testing resources that component scenarios depend on
- Component scenarios cannot access resources created by other scenarios without shared state
- Without shared state, each scenario would attempt to create/destroy its own isolated resources

**Benefits:**

- **Single infrastructure lifecycle**: Resources created once by default scenario, used by all component scenarios
- **Faster execution**: No repeated create/destroy cycles for each component scenario
- **Realistic testing environment**: Collection components often share infrastructure in production
- **Efficient resource utilization**: No duplicate resource creation
- **No need to remember command-line flags** when configured in files

**Execution flow:**

1. **default ➜ create**: Initialize shared infrastructure for ALL scenarios _(runs first)_
2. **role1 ➜ test sequence**: Component testing using shared infrastructure (no create/destroy)
3. **role2 ➜ test sequence**: Component testing using shared infrastructure (no create/destroy)
4. **role3 ➜ test sequence**: Component testing using shared infrastructure (no create/destroy)
5. **default ➜ destroy**: Clean up shared infrastructure for ALL scenarios _(runs last)_

### Per-Scenario Resources (Without shared_state)

```bash
molecule test --all
```

**How it works differently:**

- **Each scenario manages its own lifecycle**: Every scenario (including default, role1, role2, role3) runs its full test sequence including create/destroy
- **Complete isolation**: Each scenario creates and destroys its own independent resources
- **No shared infrastructure**: Scenarios cannot access resources created by other scenarios

**Characteristics:**

- Each scenario creates and destroys its own testing resources
- Complete isolation between scenarios
- Longer execution time due to repeated setup/teardown for each scenario
- Higher resource usage (4x create/destroy cycles in this example)
- Component scenarios would need their own create.yml/destroy.yml playbooks

## Running the Tests

### Development Workflow

Start with individual scenario testing during development:

```bash
# Test a specific component
molecule converge -s role1
molecule verify -s role1

# Full component test
molecule test -s role1
```

### Integration Testing

Run all scenarios together for complete collection testing:

```bash
# All scenarios with shared testing resources (configured via shared_state: true)
molecule test --all --command-borders --report
```

**Command options:**

- `--all`: Run all scenarios found in extensions/molecule/
- `--command-borders`: Visual separation of ansible-playbook executions
- `--report`: Summary report at the end

**Note:** Since `shared_state: true` is configured in the base `config.yml`, the `--shared-state` command-line flag is not required. However, it can still be used to override the configuration if needed.

### Understanding the Output

The execution flow with `--all` when shared state is enabled is:

1. **default ➜ create**: Initialize shared infrastructure for ALL scenarios _(runs first)_
2. **role1 ➜ prepare**: Satisfy role1 prerequisites
3. **role1 ➜ converge**: Execute role1
4. **role1 ➜ verify**: Validate role1 behavior
5. **role1 ➜ idempotence**: Ensure role1 is idempotent
6. **role1 ➜ verify**: Re-validate after idempotence
7. **role1 ➜ cleanup**: Clean role1 test artifacts
8. **role2 ➜ [same sequence]**: Full role2 testing (no create/destroy)
9. **role3 ➜ [same sequence]**: Full role3 testing (no create/destroy)
10. **default ➜ destroy**: Clean up shared infrastructure for ALL scenarios _(runs last)_

**Important**: Notice that:

- The default scenario's `create` action runs **first** and handles infrastructure creation for ALL scenarios
- Component scenarios (role1, role2, role3) **do not run create/destroy actions** - they only execute their test sequence using the shared infrastructure
- The default scenario's `destroy` action runs **last** and handles infrastructure cleanup for ALL scenarios
- This ensures that shared infrastructure is available throughout the entire test execution without duplication

Each step shows detailed ansible-playbook output with command borders, making it easy to identify which scenario and action is executing.

At the end of execution, Molecule provides a comprehensive summary:

```
DETAILS
default ➜ create: Executed: Successful

role1 ➜ prepare: Executed: Successful
role1 ➜ converge: Executed: Successful
role1 ➜ verify: Executed: Successful
role1 ➜ idempotence: Executed: Successful
role1 ➜ verify: Executed: Successful
role1 ➜ cleanup: Executed: Successful

role2 ➜ prepare: Executed: Successful
role2 ➜ converge: Executed: Successful
role2 ➜ verify: Executed: Successful
role2 ➜ idempotence: Executed: Successful
role2 ➜ verify: Executed: Successful
role2 ➜ cleanup: Executed: Successful

role3 ➜ prepare: Executed: Successful
role3 ➜ converge: Executed: Successful
role3 ➜ verify: Executed: Successful
role3 ➜ idempotence: Executed: Successful
role3 ➜ verify: Executed: Successful
role3 ➜ cleanup: Executed: Successful

default ➜ destroy: Executed: Successful

SCENARIO RECAP
default                   : actions=2  successful=2  disabled=0  skipped=0  missing=0  failed=0
role1                     : actions=6  successful=6  disabled=0  skipped=0  missing=0  failed=0
role2                     : actions=6  successful=6  disabled=0  skipped=0  missing=0  failed=0
role3                     : actions=6  successful=6  disabled=0  skipped=0  missing=0  failed=0
```

The **SCENARIO RECAP** provides a quick overview of test results across all scenarios, showing the total number of actions executed and their success/failure status for each scenario.
