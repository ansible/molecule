# Ansible Native Inventory Example

!!! note

    This example demonstrates the use of an ansible-native configuration.

This example demonstrates how to use native Ansible inventory sources with Molecule instead of relying on platform-based inventory generation.

## Overview

Traditional Molecule scenarios define infrastructure in the `platforms` section and let Molecule generate inventory. This example shows how to use existing Ansible inventory files and plugins directly, providing more flexibility and better integration with existing infrastructure management.

## Configuration structure

```yaml title="molecule.yml"
{!tests/fixtures/integration/test_command/molecule/native_inventory/molecule.yml!}
```

**Key points**: The `ansible_args` configuration points to the inventory directory using `${MOLECULE_SCENARIO_DIRECTORY}` environment variable. The inventory here is scenario specific but could be adjacent to the scenario directories if shared between them. These args are provided to all actions (create, converge, verify, destroy) when using user-provided playbooks, unless `MOLECULE_ANSIBLE_ARGS_STRICT_MODE` is set to revert to legacy behavior (where `ansible_args` were excluded from create/destroy actions for safety). The `default` driver indicates ansible is being used and the `platform` placeholder is not used but satisfies the schema requirements.

```yaml title="requirements.yml"
{!tests/fixtures/integration/test_command/molecule/native_inventory/requirements.yml!}
```

**Key points**: Standard collection requirements for Podman container management.

## Inventory structure

```yaml title="inventory/01-inventory.yml"
{!tests/fixtures/integration/test_command/molecule/native_inventory/inventory/01-inventory.yml!}
```

**Key points**: Static YAML inventory defining the base host `container-devtools` with its container image. The `01-` prefix ensures this loads before the constructed plugin.

```yaml title="inventory/02-constructed.yml"
{!tests/fixtures/integration/test_command/molecule/native_inventory/inventory/02-constructed.yml!}
```

**Key points**: Constructed plugin that creates the `containers` group dynamically based on hostname pattern. The `02-` prefix ensures this runs after the static inventory is loaded.

```yaml title="inventory/group_vars/containers.yml"
{!tests/fixtures/integration/test_command/molecule/native_inventory/inventory/group_vars/containers.yml!}
```

**Key points**: Sets the Ansible connection type for all hosts in the `containers` group. This applies to hosts dynamically added by the constructed plugin.

```yaml title="inventory/host_vars/container-devtools.yml"
{!tests/fixtures/integration/test_command/molecule/native_inventory/inventory/host_vars/container-devtools.yml!}
```

**Key points**: Host-specific environment variables that will be passed to the container. These demonstrate how inventory variables flow into container configuration.

## Playbook structure

### Provision resources

```yaml title="create.yml"
{!tests/fixtures/integration/test_command/molecule/native_inventory/create.yml!}
```

**Key points**: Validates that the `containers` group exists (proving the constructed plugin worked), then creates containers by looping over the dynamic group. Uses `hostvars` to access inventory variables for container configuration.

### Apply configuration changes

```yaml title="converge.yml"
{!tests/fixtures/integration/test_command/molecule/native_inventory/converge.yml!}
```

**Key points**: Targets the `containers` group created by the constructed plugin. Demonstrates how playbooks can use dynamic groups from native inventory.

### Verify configuration changes

```yaml title="verify.yml"
{!tests/fixtures/integration/test_command/molecule/native_inventory/verify.yml!}
```

### Resource

**Key points**: Uses `gather_facts: true` to access `ansible_env` for validating environment variables set from host_vars. Tests the complete inventory → container → verification flow.

### Deprovision resources

```yaml title="destroy.yml"
{!tests/fixtures/integration/test_command/molecule/native_inventory/destroy.yml!}
```

**Key points**: Loop over group members to destroy instances.

## Why Use Native Ansible Inventory?

### 1. **Leverage Existing Infrastructure**

- Use existing inventory files, scripts, and plugins
- No need to duplicate host definitions in `molecule.yml`
- Seamless integration with production inventory

### 2. **Dynamic Inventory Support**

- Use any Ansible inventory plugin (cloud providers, CMDB, etc.)
- Combine static and dynamic sources
- Real-time infrastructure discovery

### 3. **Advanced Inventory Features**

- Constructed plugin for dynamic grouping
- Complex variable hierarchies with group_vars/host_vars
- Inventory composition and merging

### 4. **Consistency**

- Same inventory format as production
- Test with actual inventory structure
- Reduce configuration drift

## Inventory File Naming Convention

Ansible loads inventory sources **alphabetically**, so naming is important:

```
inventory/
├── 01-inventory.yml    # Loaded first (static hosts)
├── 02-constructed.yml  # Loaded second (dynamic grouping)
├── group_vars/
└── host_vars/
```

**Why this order matters:**

1. `01-inventory.yml` defines the base hosts and variables
2. `02-constructed.yml` processes those hosts to create dynamic groups
3. The numeric prefixes ensure correct load order - constructed plugin needs existing hosts to process

## Key Configuration

The critical configuration is the `ansible_args` that points Ansible to the inventory directory:

```yaml
provisioner:
  name: ansible
  ansible_args:
    - --inventory=${MOLECULE_SCENARIO_DIRECTORY}/inventory/
```

This allows Ansible to automatically discover and load all inventory sources in the directory.

## Benefits Demonstrated

1. **Multiple Inventory Sources**: Static file + constructed plugin
2. **Environment Variables**: From host_vars applied to containers
3. **Dynamic Grouping**: Constructed plugin creates `containers` group
4. **Variable Hierarchy**: group_vars and host_vars working together
5. **Real Ansible Patterns**: Standard inventory structure and conventions

## Best Practices

1. **Use absolute paths** with `${MOLECULE_SCENARIO_DIRECTORY}` for inventory
2. **Name inventory files carefully** to control load order
3. **Leverage group_vars/host_vars** for clean variable organization
4. **Test dynamic groups** in create playbooks before using them
5. **Document inventory conventions** for team consistency

This approach provides much more flexibility than platform-based inventory while maintaining compatibility with existing Ansible infrastructure and patterns.
