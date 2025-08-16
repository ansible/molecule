# Ansible-Native Configuration

This document provides technical reference for the ansible-native configuration approach. The ansible-native approach leverages standard Ansible inventory, collections, and playbooks for testing resource management.

## Configuration Structure

Ansible-native molecule configurations use the following top-level sections:

```yaml
---
ansible:
  executor:
    backend: ansible-playbook
    args:
      ansible_playbook:
        - --inventory=inventory/
  env:
    ANSIBLE_FORCE_COLOR: true
  cfg:
    defaults:
      host_key_checking: false
  playbooks:
    create: create.yml
    destroy: destroy.yml
    converge: converge.yml
    verify: verify.yml

scenario:
  test_sequence:
    - create
    - converge
    - verify
    - destroy

shared_state: true

verifier:
  name: ansible
```

## Ansible Configuration Section

The `ansible` section contains all Ansible-specific configuration.

### Executor Configuration

```yaml
ansible:
  executor:
    backend: ansible-playbook
    args:
      ansible_playbook:
        - --inventory=inventory/
        - --extra-vars=environment=test
      ansible_navigator:
        - --execution-environment-image=custom:latest
        - --inventory=inventory/
```

- `backend`: Execution backend (ansible-playbook or ansible-navigator)
- `args`: Command-line arguments passed to the executor

### Environment Variables

```yaml
ansible:
  env:
    ANSIBLE_INVENTORY: inventory/
    ANSIBLE_FORCE_COLOR: true
    ANSIBLE_STDOUT_CALLBACK: yaml
    ANSIBLE_HOST_KEY_CHECKING: false
    ANSIBLE_COLLECTIONS_PATH: collections/
```

Environment variables are passed to all ansible executions. `ANSIBLE_INVENTORY` specifies the inventory source.

### Ansible Configuration

```yaml
ansible:
  cfg:
    defaults:
      inventory: inventory/
      host_key_checking: false
      fact_caching: memory
      gathering: smart
      timeout: 30
    ssh_connection:
      ssh_args: -o ControlMaster=auto -o ControlPersist=60s
      pipelining: true
```

Configuration options merged into ansible.cfg for the scenario. The `inventory` setting under defaults specifies the inventory source.

### Playbook Paths

```yaml
ansible:
  playbooks:
    create: create.yml
    destroy: destroy.yml
    converge: converge.yml
    prepare: prepare.yml
    verify: verify.yml
    cleanup: cleanup.yml
    side_effect: side_effect.yml
```

Playbook paths are relative to the scenario directory.

## Native Inventory Usage

Ansible-native approach uses standard Ansible inventory sources.

### Static YAML Inventory

#### Host-Based Testing

```yaml
# inventory/hosts.yml
all:
  children:
    web_servers:
      hosts:
        web-test-01:
          ansible_host: 192.168.1.10
          ansible_user: testuser
          ansible_ssh_private_key_file: ~/.ssh/test_key
        web-test-02:
          ansible_host: 192.168.1.11
          ansible_user: testuser
          ansible_ssh_private_key_file: ~/.ssh/test_key
      vars:
        nginx_port: 8080
        ssl_enabled: false
    database_servers:
      hosts:
        db-test-01:
          ansible_host: 192.168.1.20
          ansible_user: dbadmin
          ansible_ssh_private_key_file: ~/.ssh/test_key
      vars:
        postgresql_version: 13
        backup_enabled: false
```

#### API Endpoint Testing

```yaml
# inventory/api.yml
all:
  children:
    api_endpoints:
      hosts:
        auth-api:
          endpoint_url: https://auth-test.company.com/api/v1
          health_check_path: /health
          timeout: 30
        payment-api:
          endpoint_url: https://payment-test.company.com/api/v2
          health_check_path: /status
          timeout: 45
        user-api:
          endpoint_url: https://user-test.company.com/api/v1
          health_check_path: /ping
          timeout: 20
      vars:
        api_key: "{% raw %}{{ vault_test_api_key }}{% endraw %}"
        verify_ssl: true
        testing_environment: integration
```

#### Database Testing

```yaml
# inventory/database.yml
all:
  children:
    database_instances:
      hosts:
        postgres-test:
          db_host: postgres-test.company.com
          db_port: 5432
          db_name: test_database
          db_user: test_user
          db_password: "{% raw %}{{ vault_postgres_test_password }}{% endraw %}"
          connection_timeout: 30
        mysql-test:
          db_host: mysql-test.company.com
          db_port: 3306
          db_name: test_schema
          db_user: test_user
          db_password: "{% raw %}{{ vault_mysql_test_password }}{% endraw %}"
          connection_timeout: 15
        redis-test:
          db_host: redis-test.company.com
          db_port: 6379
          db_password: "{% raw %}{{ vault_redis_test_password }}{% endraw %}"
          connection_timeout: 10
      vars:
        testing_mode: true
        max_connections: 10
```

### Dynamic Inventory Plugin

```yaml
# inventory/dynamic.yml
plugin: amazon.aws.aws_ec2
regions:
  - us-east-1
filters:
  "tag:Environment": "test" # Only instances with tag Environment=test
keyed_groups:
  - key: tags.Name
    prefix: tag
```

### Constructed Inventory

```yaml
# inventory/constructed.yml
plugin: constructed
strict: false
compose:
  ansible_host: ansible_host | default(inventory_hostname)
  component_role: group_names | select('match', '^role_') | first | default('undefined')
groups:
  web_servers: "'web' in component_type"
  database_servers: "'database' in component_type"
  testing: "environment == 'test'"
```

### Enterprise Inventory Integration

```yaml
# inventory/enterprise.yml
all:
  vars:
    ansible_user: "{% raw %}{{ vault_ssh_user }}{% endraw %}"
    ansible_ssh_private_key_file: "{% raw %}{{ vault_ssh_key_path }}{% endraw %}"
    aws_region: us-east-1
    aws_access_key_id: "{% raw %}{{ vault_aws_access_key }}{% endraw %}"
    aws_secret_access_key: "{% raw %}{{ vault_aws_secret_key }}{% endraw %}"
    cmdb_base_url: "https://cmdb.internal.company.com/api/v1"
    servicenow_instance: "https://company.service-now.com"
    servicenow_username: "{% raw %}{{ vault_servicenow_user }}{% endraw %}"
    servicenow_password: "{% raw %}{{ vault_servicenow_password }}{% endraw %}"
    monitoring_enabled: true
    compliance_profile: enterprise
  children:
    test:
      hosts:
        web-test-01.company.com:
          ansible_host: 10.0.1.10
          datacenter: us-east-1a
          aws_instance_id: i-0123456789abcdef0
          aws_instance_type: t3.medium
          servicenow_ci: 12345678-1234-1234-1234-123456789abc
          load_balancer_weight: 100
          ssl_cert_name: "{% raw %}{{ vault_ssl_cert_web_test }}{% endraw %}"
        db-test-01.company.com:
          ansible_host: 10.0.2.10
          datacenter: us-east-1a
          aws_instance_id: i-0abcdef123456789a
          aws_instance_type: r5.large
          servicenow_ci: abcdef12-3456-7890-abcd-ef1234567890
          db_master: true
          db_backup_schedule: "0 2 * * *"
          db_password: "{% raw %}{{ vault_db_password_test }}{% endraw %}"
      vars:
        environment: test
        backup_enabled: false
```

## Shared State Configuration

Shared state enables scenarios to share ephemeral state and testing resources.

### Configuration

```yaml
shared_state: true
```

When enabled:

- All scenarios share the same ephemeral state directory
- Default scenario manages testing resource lifecycle
- Component scenarios access shared resources
- State persists between scenario executions

### Resource Lifecycle Management

**Default scenario** (testing resource management):

```yaml
scenario:
  test_sequence:
    - create
    - destroy
```

**Component scenarios** (testing only):

```yaml
scenario:
  test_sequence:
    - prepare
    - converge
    - verify
    - cleanup
```

### Execution Flow

With `shared_state: true`:

1. Default scenario creates shared testing resources
2. Component scenarios execute tests against shared resources
3. Default scenario destroys shared testing resources

## Collection-Based Resource Management

The ansible-native approach leverages ansible collections for testing resource management.

### Container Testing Resources

```yaml
# create.yml
---
- name: Create testing containers
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Create container network
      containers.podman.podman_network:
        name: molecule-test
        state: present

    - name: Create test containers
      containers.podman.podman_container:
        name: "{% raw %}{{ item }}{% endraw %}"
        image: "{% raw %}{{ hostvars[item].image }}{% endraw %}"
        state: started
        networks:
          - molecule-test
        published_ports:
          - "{% raw %}{{ hostvars[item].port | default('0') }}:{{ hostvars[item].internal_port | default('80') }}{% endraw %}"
      loop: "{% raw %}{{ groups['test_resources'] }}{% endraw %}"

    - name: Wait for containers
      ansible.builtin.wait_for:
        port: "{% raw %}{{ hostvars[item].internal_port | default('80') }}{% endraw %}"
        host: "{% raw %}{{ hostvars[item].ansible_host }}{% endraw %}"
        delay: 5
      loop: "{% raw %}{{ groups['test_resources'] }}{% endraw %}"
```

### Cloud Testing Resources

```yaml
# create.yml
---
- name: Create AWS testing resources
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Create VPC
      amazon.aws.ec2_vpc_net:
        name: molecule-test-vpc
        cidr_block: 10.0.0.0/16
        region: "{% raw %}{{ aws_region }}{% endraw %}"
        state: present
      register: vpc

    - name: Create security group
      amazon.aws.ec2_security_group:
        name: molecule-test-sg
        description: Molecule testing security group
        vpc_id: "{% raw %}{{ vpc.vpc.id }}{% endraw %}"
        region: "{% raw %}{{ aws_region }}{% endraw %}"
        rules:
          - proto: tcp
            ports:
              - 22
              - 80
            cidr_ip: 0.0.0.0/0
        state: present
      register: sg

    - name: Launch instances
      amazon.aws.ec2_instance:
        name: "{% raw %}{{ item }}{% endraw %}"
        image_id: "{% raw %}{{ hostvars[item].ami_id }}{% endraw %}"
        instance_type: "{% raw %}{{ hostvars[item].instance_type }}{% endraw %}"
        vpc_subnet_id: "{% raw %}{{ vpc.vpc.id }}{% endraw %}"
        security_group: "{% raw %}{{ sg.group_id }}{% endraw %}"
        region: "{% raw %}{{ aws_region }}{% endraw %}"
        state: started
        wait: true
      loop: "{% raw %}{{ groups['test_resources'] }}{% endraw %}"
```

### Collection Dependencies

```yaml
# requirements.yml
---
collections:
  - name: containers.podman
    version: ">=1.9.0"
  - name: amazon.aws
    version: ">=5.0.0"
  - name: community.general
    version: ">=6.0.0"
```

## Scenario Types

### Collection Component Testing

Test individual collection components (roles, modules, plugins):

```yaml
# molecule.yml
---
ansible:
  executor:
    args:
      ansible_playbook:
        - --inventory=inventory/
  playbooks:
    converge: converge.yml
    verify: verify.yml

scenario:
  test_sequence:
    - converge
    - verify
    - idempotence
```

```yaml
# converge.yml
---
- name: Test collection role
  hosts: test_resources
  tasks:
    - name: Include collection role
      ansible.builtin.include_role:
        name: my_namespace.my_collection.my_role
      vars:
        role_config: test_value
```

### Playbook Testing

Test complete playbooks:

```yaml
# converge.yml
---
- name: Execute test playbook
  ansible.builtin.import_playbook: "{% raw %}{{ molecule_project_directory }}{% endraw %}/playbooks/site.yml"
```

### Multi-Scenario Collection Testing

```yaml
# Base config.yml
---
ansible:
  executor:
    args:
      ansible_playbook:
        - --inventory={% raw %}{{ molecule_scenario_directory }}{% endraw %}/../inventory/

scenario:
  test_sequence:
    - converge
    - verify

shared_state: true
```

**Default scenario** manages testing resources:

```yaml
# default/molecule.yml
---
scenario:
  test_sequence:
    - create
    - destroy
```

**Component scenarios** inherit base configuration and test specific components.

### Integration Testing Patterns

Multi-component testing with shared resources:

```yaml
# verify.yml
---
- name: Integration tests
  hosts: web_servers
  tasks:
    - name: Test web service responds
      ansible.builtin.uri:
        url: "http://{% raw %}{{ ansible_host }}{% endraw %}:80/health"
        method: GET
        status_code: 200

    - name: Test database connectivity
      ansible.builtin.wait_for:
        host: "{% raw %}{{ hostvars[groups['database_servers'][0]].ansible_host }}{% endraw %}"
        port: 5432
        timeout: 10

- name: Cross-component tests
  hosts: test_resources
  tasks:
    - name: Verify service mesh communication
      ansible.builtin.uri:
        url: "http://{% raw %}{{ ansible_host }}{% endraw %}/api/status"
        return_content: true
      register: api_response

    - name: Assert response format
      ansible.builtin.assert:
        that:
          - api_response.json.status == "healthy"
          - api_response.json.version is defined
```

## Verifier Configuration

The ansible verifier executes verification playbooks using the same inventory and configuration as other testing phases.

### Basic Configuration

```yaml
verifier:
  name: ansible
  enabled: true
```

### Environment Variables

Environment variables for verification should be configured in the `ansible` section:

```yaml
ansible:
  env:
    PYTHONPATH: /custom/test/path
    TEST_DATABASE_URL: postgresql://test:test@localhost/test
    ANSIBLE_FORCE_COLOR: true
```

Verification playbooks have access to all molecule environment variables and scenario configuration.

## Complete Example

```yaml
---
ansible:
  executor:
    backend: ansible-playbook
    args:
      ansible_playbook:
        - --inventory=inventory/
        - --extra-vars=test_mode=true
  env:
    ANSIBLE_FORCE_COLOR: true
    ANSIBLE_HOST_KEY_CHECKING: false
  cfg:
    defaults:
      fact_caching: memory
      gathering: smart
  playbooks:
    create: create.yml
    destroy: destroy.yml
    converge: converge.yml
    verify: verify.yml

scenario:
  test_sequence:
    - create
    - converge
    - verify
    - destroy

shared_state: true

verifier:
  name: ansible
```

This configuration defines ansible-native testing with:

- Native inventory sources in `inventory/` directory
- Collection-based testing resource management in create/destroy playbooks
- Shared state for multi-scenario testing
- Standard ansible verification
- Custom environment variables and configuration options

## Supplemental Inventory Generation

In the ansible-native approach, Molecule generates only a supplemental inventory file containing molecule-specific variables that are made available to playbooks. This includes environment variables like `MOLECULE_SCENARIO_DIRECTORY`, `MOLECULE_EPHEMERAL_DIRECTORY`, and scenario metadata. The primary inventory comes from the sources specified in `ansible.executor.args.ansible_playbook`, allowing full integration with existing inventory management systems while maintaining Molecule's testing capabilities.
