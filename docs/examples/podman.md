# Using podman containers

!!! note

    This example demonstrates the use of an ansible-native configuration.

This example demonstrates testing with Podman containers using standard Ansible inventory and playbooks for complete control over the testing environment.

## Overview

This scenario uses:

- **Inventory management**: Standard Ansible inventory files for container definitions
- **Container lifecycle**: Managed through Ansible playbooks with full customization
- **Flexible configuration**: Container settings defined in inventory for easy modification

When you run `molecule test --scenario-name podman`, Molecule executes the complete test sequence including create, converge, verify, cleanup, and destroy steps using your custom playbooks.

## Configuration

The configuration uses standard Ansible patterns:

```yaml title="molecule.yml"
{!tests/fixtures/integration/test_command/molecule/podman/molecule.yml!}
```

**Key points**: The `ansible` section configures inventory location and executor arguments. The `default` driver indicates pure Ansible automation without Molecule-specific drivers.

```yaml title="requirements.yml"
{!tests/fixtures/integration/test_command/molecule/podman/requirements.yml!}
```

## Inventory Structure

Container definitions are managed through standard Ansible inventory:

```yaml title="inventory/hosts.yml"
{!tests/fixtures/integration/test_command/molecule/podman/inventory/hosts.yml!}
```

**Key points**: Containers are defined as inventory hosts with connection and configuration details. The `molecule` group contains test targets.

```yaml title="inventory/group_vars/molecule.yml"
{!tests/fixtures/integration/test_command/molecule/podman/inventory/group_vars/molecule.yml!}
```

**Key points**: Group variables provide shared configuration for container settings.

## Lifecycle Playbooks

### Create Playbook

```yaml title="create.yml"
{!tests/fixtures/integration/test_command/molecule/podman/create.yml!}
```

**Key points**: Creates containers based on inventory definitions using `hostvars` for configuration. Includes error handling and connection verification.

```yaml title="tasks/create-fail.yml"
{!tests/fixtures/integration/test_command/molecule/podman/tasks/create-fail.yml!}
```

**Key points**: Error handling task that displays container logs when creation fails.

### Converge Playbook

```yaml title="converge.yml"
{!tests/fixtures/integration/test_command/molecule/podman/converge.yml!}
```

**Key points**: Validates inventory structure, gathers facts from containers, reads OS information, and writes data to a temporary file for verification. Uses proper Ansible modules instead of raw commands thanks to the Python-enabled container image.

### Verify Playbook

```yaml title="verify.yml"
{!tests/fixtures/integration/test_command/molecule/podman/verify.yml!}
```

**Key points**: Reads the temporary file created during converge, verifies the container OS is Fedora-based, and validates the dev tools environment variable. Demonstrates comprehensive container testing and validation.

### Cleanup Playbook

```yaml title="cleanup.yml"
{!tests/fixtures/integration/test_command/molecule/podman/cleanup.yml!}
```

**Key points**: Intelligently removes temporary files created during testing, but only when containers exist and are running. Includes robust error handling for edge cases.

### Destroy Playbook

```yaml title="destroy.yml"
{!tests/fixtures/integration/test_command/molecule/podman/destroy.yml!}
```

**Key points**: Cleanly removes containers using inventory host definitions with error handling.

## Benefits

- **Standard practices**: Uses familiar Ansible inventory and playbook patterns
- **Full control**: Complete customization of container lifecycle and configuration
- **Modern tooling**: Leverages Python-enabled container images for full Ansible module support
- **Comprehensive testing**: Includes converge, verify, and cleanup phases for thorough validation
- **Reusable**: Inventory can be shared across multiple scenarios
- **Maintainable**: Clear separation of concerns between configuration and automation
- **Flexible**: Easy to extend with additional container settings, networking, or testing logic
- **Robust**: Intelligent error handling and conditional execution for reliable testing

This approach provides the foundation for more complex testing scenarios while maintaining simplicity and demonstrating modern ansible-native practices with comprehensive lifecycle management.
