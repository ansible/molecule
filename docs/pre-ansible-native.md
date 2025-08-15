# Pre Ansible-Native Configuration

The pre ansible-native approach is maintained for compatibility with environments that still rely on third-party tools and pre ansible-native configurations. This document provides technical reference for the these configuration constructs: platforms, drivers, and provisioner sections.


## Configuration Structure

Pre ansible-native molecule configurations use the following top-level sections:

```yaml
---
driver:
  name: default
platforms:
  - name: instance
provisioner:
  name: ansible
verifier:
  name: ansible
scenario:
  name: default
```

## Platforms

The `platforms` section defines the target instances for testing. Molecule uses this information to generate inventory and manage instance lifecycle.

### Basic Platform Definition

```yaml
platforms:
  - name: instance-1
    groups:
      - web_servers
    children:
      - child_group
```

### Platform Properties

Each platform supports the following common properties:

- `name`: Unique identifier for the instance
- `hostname`: Override the hostname (defaults to name)
- `groups`: List of Ansible inventory groups to assign
- `children`: List of child groups for inventory hierarchy

### Driver-Specific Properties

Additional properties depend on the driver being used. Common container platform properties:

```yaml
platforms:
  - name: ubuntu-20-04
    image: ubuntu:20.04
    command: /sbin/init
    privileged: true
    hostname: custom-hostname
    memory: 1024
    cpus: 2
    env:
      CUSTOM_VAR: value
    environment:
      DATABASE_URL: postgres://localhost
    networks:
      - name: custom_network
        aliases:
          - app-server
        ipv4_address: 192.168.1.10
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:ro
    tmpfs:
      - /run
      - /tmp
    ulimits:
      - nofile:1024:2048
    network_mode: bridge
    cgroupns_mode: private
    pre_build_image: true
    pkg_extras: python3-pip
    registry:
      url: registry.example.com
      credentials:
        username: user
        password: pass
```

Additional platform properties include `interfaces`, `box` (for Vagrant), `provider_options`, and `provider_raw_config_args`. Driver-specific properties are passed through to the driver implementation without validation by the core Molecule schema.

### Multiple Platforms

```yaml
platforms:
  - name: centos-8
    image: centos:8
    groups:
      - centos
  - name: ubuntu-20-04
    image: ubuntu:20.04
    groups:
      - ubuntu
  - name: debian-11
    image: debian:11
    groups:
      - debian
```

**Ansible-native approach:** Infrastructure is managed through native Ansible inventory files and plugins instead of platform definitions. Configuration moves to `ansible.executor.args` pointing to inventory sources.

## Driver

The `driver` section specifies which driver manages instance lifecycle. Molecule delegates create/destroy operations to the configured driver.

### Default Driver

```yaml
driver:
  name: podman
  options:
    managed: true
```

The `default` driver indicates that ansible will handle infrastructure management through user-provided create/destroy playbooks.

### Driver Options

```yaml
driver:
  name: default
  options:
    managed: false
    login_cmd_template: "docker exec -ti {instance} bash"
    ansible_connection_options:
      ansible_connection: ssh
      ansible_user: root
```

- `managed`: Whether Molecule manages instance lifecycle (default: true)
- `login_cmd_template`: Template for login command when using `molecule login`
- `ansible_connection_options`: Connection parameters for Ansible

### External Drivers

Community-supported drivers provide additional functionality through the [molecule-plugins](https://github.com/ansible-community/molecule-plugins) collection:

```yaml
driver:
  name: docker
  options:
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
```

```yaml
driver:
  name: podman
  options:
    network: host
```

See the [molecule-plugins](https://github.com/ansible-community/molecule-plugins) repository for available community drivers and installation instructions.

**Ansible-native approach:** The `default` driver is used with engineer-provided create/destroy playbooks, eliminating the need for third-party driver plugins. Driver-specific configuration is replaced by standard Ansible playbook logic.

### Why Drivers Exist

Drivers were created to abstract infrastructure provisioning across different platforms (Docker, Podman, AWS EC2, Azure, etc.) without requiring engineers to write custom create/destroy playbooks for each environment. Each driver encapsulates the platform-specific logic for instance lifecycle management, connection details, and inventory generation. This allowed Molecule to support multiple testing environments through a consistent interface, where engineers could switch between local containers and cloud instances by simply changing the driver name in their configuration.

The combination of ansible-native inventories and content within ansible collections now displaces the need for drivers. Collections provide standardized modules and plugins for infrastructure management, while native inventory systems handle connection details and host organization. This allows engineers to write standard Ansible playbooks using collection modules (like `containers.podman.podman_container` or `amazon.aws.ec2_instance`) instead of relying on driver-specific abstractions.

## Provisioner

The `provisioner` section configures how Molecule invokes Ansible for testing operations.

### Basic Provisioner Configuration

```yaml
provisioner:
  name: ansible
  log: true
```

### Ansible Configuration Options

```yaml
provisioner:
  name: ansible
  config_options:
    defaults:
      host_key_checking: false
      fact_caching: jsonfile
      fact_caching_connection: /tmp/molecule/facts
    inventory:
      enable_plugins: host_list, script, auto, yaml, ini
```

### Environment Variables

```yaml
provisioner:
  name: ansible
  env:
    ANSIBLE_STDOUT_CALLBACK: yaml
    ANSIBLE_FORCE_COLOR: true
    ANSIBLE_VERBOSITY: 2
```

### Playbook Paths

```yaml
provisioner:
  name: ansible
  playbooks:
    create: create.yml
    destroy: destroy.yml
    converge: converge.yml
    prepare: prepare.yml
    side_effect: side_effect.yml
    verify: verify.yml
    cleanup: cleanup.yml
```

### Inventory Configuration

```yaml
provisioner:
  name: ansible
  inventory:
    hosts:
      all:
        hosts:
          instance-1:
            ansible_python_interpreter: /usr/bin/python3
        vars:
          custom_var: value
      web_servers:
        vars:
          http_port: 80
    host_vars:
      instance-1:
        role_var: specific_value
    group_vars:
      web_servers:
        service_name: httpd
    links:
      - /path/to/group_vars/
      - /path/to/host_vars/
```

### Connection Options

```yaml
provisioner:
  name: ansible
  connection_options:
    ansible_ssh_user: root
    ansible_ssh_common_args: -o IdentitiesOnly=no
    ansible_ssh_private_key_file: /path/to/key
```

### Ansible Arguments

```yaml
provisioner:
  name: ansible
  ansible_args:
    - --inventory=custom.yml
    - --limit=subset
    - --check
```

**Note:** In the ansible-native approach, several provisioner keys (`ansible_args`, `config_options`, `env`, `playbooks`) have been migrated to the `ansible` root section.

**Ansible-native approach:** Provisioner configuration moves to the `ansible` root section with `executor.args`, `env`, and `cfg` subsections. Playbook paths and inventory configuration are handled through standard Ansible mechanisms.

## Verifier

The `verifier` section configures test execution and validation.

### Ansible Verifier

```yaml
verifier:
  name: ansible
  enabled: true
```

The ansible verifier executes `verify.yml` playbooks containing test assertions.

### Testinfra Verifier

```yaml
verifier:
  name: testinfra
  enabled: true
  options:
    verbose: true
    capture: no
  additional_files_or_dirs:
    - test_*.py
    - tests/
```

Testinfra verifier executes Python-based tests. It requires separate installation as an optional dependency.



### Verifier Options

```yaml
verifier:
  name: testinfra
  options:
    verbose: true
    capture: no
    tb: short
  env:
    PYTHONPATH: /custom/path
```

**Ansible-native approach:** Verification remains as `verifier.name: ansible` but relies on standard Ansible playbooks and inventory rather than generated inventory from platforms.



## Generated Inventory

When using platforms configuration, Molecule generates Ansible inventory automatically based on platform definitions and groups.

### Generated Structure

```yaml
all:
  hosts:
    instance-1:
      ansible_host: 172.17.0.2
    instance-2:
      ansible_host: 172.17.0.3
  children:
    web_servers:
      hosts:
        instance-1: {}
    database_servers:
      hosts:
        instance-2: {}
    frontend:
      hosts:
        instance-1: {}
      children:
        web_servers: {}
```

### Host Variables

Platform-specific variables and driver connection details are automatically added to the generated inventory.

**Ansible-native approach:** Generated inventory is replaced by native Ansible inventory files, plugins, and directories managed directly through Ansible's inventory system.

## Complete Example

```yaml
---
driver:
  name: default
  options:
    managed: true

platforms:
  - name: web-server
    image: nginx:alpine
    groups:
      - web_servers
    port_bindings:
      8080: 80
  - name: db-server
    image: postgres:13
    groups:
      - database_servers
    environment:
      POSTGRES_PASSWORD: test

provisioner:
  name: ansible
  config_options:
    defaults:
      host_key_checking: false
  env:
    ANSIBLE_STDOUT_CALLBACK: yaml
  inventory:
    host_vars:
      web-server:
        nginx_port: 80
    group_vars:
      database_servers:
        db_port: 5432

verifier:
  name: ansible

scenario:
  test_sequence:
    - create
    - prepare
    - converge
    - verify
    - destroy
```

This configuration defines a two-instance setup with web and database servers, custom inventory variables, and the standard test sequence.

## Ansible-Native Inventory Usage

In the ansible-native approach, Molecule uses existing Ansible inventory sources (files, directories, plugins) specified through `ansible.executor.args.ansible_playbook` configuration. Molecule only generates a supplemental inventory file containing molecule-specific variables that are made available to playbooks, such as `MOLECULE_*` environment variables and scenario metadata. This allows full integration with existing inventory management systems while maintaining Molecule's testing capabilities.
