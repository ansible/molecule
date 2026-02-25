# Testing philosophy

This document explores the fundamental principles of automation testing and how Molecule addresses the core needs of modern Ansible development across all domains.

## What a testing suite provides

Testing frameworks serve as the foundation for reliable software development and deployment across diverse domains. Whether developing applications, managing infrastructure, configuring systems, orchestrating deployments, or integrating with external services, a comprehensive testing suite addresses several critical areas that ensure code quality, operational confidence, and maintainable systems.

### Essential functionality requirements

**Resource lifecycle management**
Testing requires precise control over test environments, whether they're compute resources, application instances, database states, test data, or external service configurations. This includes the ability to create clean, isolated environments for each test run, manage their state throughout the testing process, and reliably tear them down afterward. The framework must handle dependencies between components, ensure proper cleanup even when tests fail, and provide mechanisms for debugging by preserving failed environments when needed.

**Test isolation and reproducibility**
Each test must run in a predictable, isolated environment that doesn't interfere with other tests or external systems. For infrastructure testing, this means isolated compute resources. For application testing, this requires consistent application states and configuration baselines. For integration testing, this involves controlled staging environments. For API testing, this includes isolated service endpoints or mocked external dependencies. Reproducibility ensures that test results remain consistent across different execution environments, team members, and CI/CD pipelines regardless of the testing domain.

**Flexible execution strategies**
Modern development workflows demand flexibility in how and when tests execute. This includes support for different test sequences (syntax validation, unit testing, integration testing, end-to-end scenarios), selective test execution for rapid development cycles, parallel processing capabilities for complex multi-component systems, and the ability to share state between related tests when appropriate. The framework must accommodate both developer workflows (quick iteration on code changes) and automated pipeline requirements (comprehensive validation before deployment).

**Configuration adaptability**
Testing frameworks must support diverse patterns and use cases. This includes multiple platform support (from bare metal to cloud to containers), configurable provisioning strategies (infrastructure, applications, services), environment-specific variable management (development, staging, production), and integration with existing toolchains (CI/CD, monitoring, secret management, external APIs). The configuration system should be both powerful enough for complex multi-tier applications and simple enough for basic testing scenarios.

### Configuration flexibility requirements

**Multi-platform support**
Software systems span diverse platforms and domains: infrastructure (containers, VMs, cloud services, bare metal), applications (web servers, databases, microservices), network devices (routers, switches, firewalls), cloud services (AWS, Azure, GCP), and external systems (REST APIs, SaaS platforms, monitoring tools). Testing frameworks must abstract platform differences while allowing domain-specific optimizations. This includes unified interfaces for common operations, platform-specific configuration options, and consistent behavior across different testing domains.

**Variable and secret management**
Testing environments require careful handling of configuration data, secrets, and environment-specific variables across all testing domains. This includes database connection strings, API keys, service endpoints, infrastructure credentials, application configuration parameters, and environment-specific overrides. The framework must provide secure secret injection, hierarchical variable override systems, environment-specific configuration, and integration with external secret management systems while supporting the diverse credential types needed for comprehensive testing.

**Extensibility and integration**
Testing frameworks serve as components in larger development ecosystems spanning infrastructure, applications, and business processes. They must integrate cleanly with CI/CD pipelines, monitoring systems, artifact repositories, development tools, deployment platforms, and external service providers. This requires well-defined APIs, plugin architectures, standardized output formats that other tools can consume, and the ability to coordinate with diverse external systems that modern software development typically interacts with.

### Lifecycle management capabilities

**Environment provisioning**
The framework must create test environments that accurately reflect production conditions while remaining cost-effective and fast to provision. For infrastructure testing, this includes compute resources, networking, and storage. For application testing, this involves application instances, databases, and service dependencies. For API integration testing, this requires mock services or sandboxed external systems. For system testing, this includes multi-tier environments with realistic data flows. The framework must support template-based provisioning, dependency management, network isolation, and resource quota management across all these domains.

**State management**
Complex testing scenarios require sophisticated state management across multiple domains. This includes checkpointing successful infrastructure states, preserving application configurations between test phases, maintaining database states for integration testing, managing external service interactions, and coordinating state across distributed systems. The framework must support sharing state between test phases, managing concurrent access to shared resources, and providing rollback capabilities when tests fail unexpectedly, regardless of whether the testing targets infrastructure, applications, or external services.

**Cleanup and resource recovery**
Reliable cleanup prevents resource leaks and ensures consistent test environments across all testing domains. The framework must track all created resources (infrastructure, application instances, database entries, external service configurations), handle cleanup in the presence of failures, provide manual cleanup tools for debugging, and integrate with monitoring systems to detect orphaned resources. This includes cleaning up cloud resources, stopping application services, resetting database states, and reverting external system configurations.

**Observability and debugging**
When tests fail, teams need comprehensive visibility into what happened across all system layers. This includes detailed logging from infrastructure provisioning, application deployment logs, API interaction traces, configuration change tracking, and performance metrics. The framework must support artifact collection (logs, configurations, state dumps), state snapshots at multiple levels, and integration with debugging tools. It should make it easy to reproduce failures locally and provide enough context to quickly identify root causes whether they stem from infrastructure issues, application configuration problems, external service failures, or system logic errors.

## Testing workflow fundamentals

Effective testing follows a structured workflow that ensures comprehensive validation while maintaining efficiency and reliability. This workflow applies across all testing domains, from unit testing to integration testing to end-to-end system validation.

### Core testing phases

**Environment provisioning**
The testing process begins with creating clean, isolated environments that accurately represent production conditions. This includes provisioning infrastructure resources (compute, networking, storage), deploying application dependencies (databases, message queues, caching layers), and configuring external service connections (APIs, monitoring endpoints, third-party integrations). The provisioning phase must be fast enough for developer workflows while being comprehensive enough to catch environment-specific issues.

**Dependency resolution**
Before executing the system under test, the testing framework must ensure all required dependencies are available. This includes software modules, external libraries, configuration files, secrets, and any prerequisite services. Dependency resolution must handle version constraints, conflict detection, and both public and private repositories while supporting offline development scenarios.

**Change application and convergence**
The core testing phase applies the system logic being tested. This involves executing scripts, configurations, or procedures against the test environment and ensuring they complete successfully. The framework must capture detailed execution logs, handle failures gracefully, and provide mechanisms for incremental development and debugging. This phase validates that the system logic works correctly in realistic conditions.

**Idempotence verification**
A critical aspect of system testing involves verifying that operations can be run multiple times without causing unintended changes. The framework must re-execute the same system logic and confirm that no changes occur on subsequent runs. This validates that the system properly detects existing states and only makes necessary modifications, preventing drift and ensuring predictable behavior.

**Functional verification**
After applying changes, the testing framework must validate that the desired outcomes were achieved. This includes verifying infrastructure states (resources created, configurations applied), application behavior (services running, endpoints responding), integration functionality (APIs accessible, data flowing correctly), and business process outcomes (workflows completing, notifications sent). Verification must be comprehensive enough to catch subtle issues while being fast enough for rapid iteration.

**Side effect detection**
System changes can have unintended consequences beyond their primary objectives. The testing framework must detect side effects such as unexpected resource modifications, service disruptions, security policy changes, performance impacts, or external system effects. This phase helps identify potential issues before they impact production environments.

**Resource cleanup and destruction**
The final phase involves cleaning up all resources created during testing. This includes infrastructure resources, application instances, database entries, temporary files, external service configurations, and any other artifacts created during the test process. Proper cleanup prevents resource leaks, controls costs, and ensures clean states for subsequent test runs.

### Testing strategy considerations

**Isolation vs. efficiency trade-offs**
Testing frameworks must balance complete isolation (which ensures clean tests but increases resource usage and execution time) with resource sharing (which improves efficiency but introduces potential cross-test dependencies). The optimal strategy depends on the specific automation being tested, available resources, and team workflows.

**Incremental vs. comprehensive testing**
During development, teams need fast feedback loops that validate changes quickly. In CI/CD pipelines, comprehensive testing ensures production readiness. The framework must support both incremental testing (validating specific changes) and comprehensive testing (full end-to-end validation) while allowing teams to choose appropriate strategies for different contexts.

**State preservation vs. fresh environments**
Some testing scenarios benefit from preserving state between test phases (performance testing, migration validation, integration testing), while others require completely fresh environments (unit testing, isolation verification). The framework must support both approaches and allow teams to choose based on their specific testing requirements.

## How Molecule addresses testing suite requirements

Molecule specifically addresses the unique challenges of testing Ansible automation across all domains while providing the comprehensive testing suite capabilities outlined above. The framework's design reflects deep understanding of both general testing principles and the specific needs of modern automation, whether targeting infrastructure, applications, deployments, integrations, or business processes.

### Ansible-centric testing design

**Playbook-driven lifecycle management**
Molecule leverages Ansible's declarative nature by using playbooks to manage the entire test lifecycle across all automation domains. Whether testing infrastructure provisioning, application deployment, configuration management, or external service integration, this approach ensures consistency between test environments and production patterns while providing familiar syntax for Ansible practitioners. The same playbook constructs used for production automation can be used for test environment setup, making tests more representative of real-world usage.

**Native integration with Ansible constructs**
Rather than wrapping Ansible as an external tool, Molecule integrates directly with Ansible's inventory system, variable hierarchy, and module ecosystem. This tight integration includes native support for external inventory sources, allowing teams to test using existing inventory patterns, dynamic inventory scripts, and inventory plugins. The framework works seamlessly whether you're testing infrastructure modules (cloud resources, networking), application modules (services, configurations), integration modules (APIs, databases), or custom modules. This eliminates impedance mismatches and ensures that test environments accurately reflect production Ansible usage patterns regardless of the automation domain.

### Sequence configuration and workflow control

**Testing phase to action mapping**
Molecule implements the core testing phases through a comprehensive action system that maps directly to testing workflow fundamentals:

| Testing Phase            | Molecule Action | Purpose                                                            |
| ------------------------ | --------------- | ------------------------------------------------------------------ |
| Environment provisioning | `create`        | Provisions test infrastructure and environments                    |
| Dependency resolution    | `dependency`    | Installs required roles, collections, and dependencies             |
| Environment preparation  | `prepare`       | Configures environments before applying automation logic           |
| Change application       | `converge`      | Executes the automation being tested                               |
| Idempotence verification | `idempotence`   | Re-runs automation to verify no unintended changes                 |
| Side effect detection    | `side_effect`   | Executes additional automation to test for unintended consequences |
| Functional verification  | `verify`        | Validates that desired outcomes were achieved                      |
| Resource cleanup         | `cleanup`       | Removes temporary files and intermediate artifacts                 |
| Resource destruction     | `destroy`       | Cleans up all provisioned resources                                |

**Configurable test sequences**
Molecule's sequence system provides fine-grained control over test execution flow by allowing teams to define custom sequences that match their specific testing requirements. Since its inception in 2015, Molecule's default sequences have been optimized through real-world usage at scale to satisfy most users' testing workflows. However, enterprise environments often have specific workflow requirements that differ from these defaults. Molecule addresses this by allowing sequences to be modified, committed as part of the codebase, and shared between team members, ensuring consistent testing approaches across development teams. Actions can be reordered, removed, or repeated based on testing needs:

```yaml
# Full comprehensive testing sequence
scenario:
  test_sequence:
    - dependency      # Install requirements
    - create         # Provision environment
    - prepare        # Configure environment
    - converge       # Apply automation
    - idempotence    # Verify idempotence
    - side_effect    # Test side effects
    - verify         # Functional verification
    - cleanup        # Clean temporary artifacts
    - destroy        # Remove all resources

# Rapid development sequence (skips verification phases)
scenario:
  test_sequence:
    - dependency
    - create
    - converge
    - destroy

# Integration testing sequence (preserves state between phases)
scenario:
  test_sequence:
    - dependency
    - create
    - prepare
    - converge
    - verify
    - side_effect
    - verify
    # Note: cleanup and destroy omitted for state preservation
```

**Command-line subcommand mapping**
Each action in a test sequence corresponds to a specific `molecule` subcommand, allowing developers to execute individual phases during development while ensuring complete automated testing in CI/CD pipelines:

| Command                | Action                          | Usage                                          |
| ---------------------- | ------------------------------- | ---------------------------------------------- |
| `molecule dependency`  | Installs roles and collections  | Development setup and CI/CD preparation        |
| `molecule create`      | Provisions test environments    | Environment setup for all testing phases       |
| `molecule prepare`     | Configures test environments    | Custom environment preparation                 |
| `molecule converge`    | Applies automation being tested | Core development and validation workflow       |
| `molecule idempotence` | Verifies idempotent behavior    | Quality assurance and CI/CD validation         |
| `molecule side_effect` | Tests for unintended effects    | Comprehensive testing and regression detection |
| `molecule verify`      | Validates expected outcomes     | Functional testing and acceptance criteria     |
| `molecule cleanup`     | Removes temporary artifacts     | Resource management and cost optimization      |
| `molecule destroy`     | Cleans up all resources         | Environment teardown and reset                 |
| `molecule test`        | Runs complete sequence          | Full automated testing workflow                |

**Selective execution and debugging**
Developers can execute any subset of the test sequence, enabling rapid iteration during development and focused debugging when tests fail. This flexibility supports both quick feedback loops (testing playbook logic changes) and comprehensive validation (full deployment workflows):

```bash
# Quick development iteration
molecule converge  # Apply changes
molecule verify    # Check outcomes

# Debug environment issues
molecule create    # Set up environment
molecule prepare   # Configure environment
# Manually investigate environment state

# Test idempotence specifically
molecule converge  # Apply automation
molecule idempotence  # Verify no changes on re-run

# Full comprehensive testing
molecule test      # Run complete sequence
```

### Native inventory integration and management

**Direct integration with Ansible inventory systems**
Molecule provides comprehensive support for native Ansible inventory integration, enabling teams to test automation against existing inventory sources rather than relying solely on Molecule-generated inventory from platform configurations. This native inventory capability allows testing automation against the same inventory systems and patterns used in production environments, ensuring true production parity while testing against appropriate lab, staging, or test systems.

**External inventory sources**
Molecule supports the full spectrum of Ansible inventory sources through direct integration with the `ansible-playbook` command:

- **Static inventory files**: Use existing YAML or INI inventory files that define lab, staging, or test resources
- **Dynamic inventory scripts**: Leverage cloud provider inventories, CMDB systems, or custom inventory scripts
- **Inventory plugins**: Integration with Ansible's inventory plugin ecosystem (AWS, Azure, GCP, Kubernetes, etc.)
- **Constructed inventories**: Dynamic grouping and variable assignment based on existing inventory data
- **Mixed inventory sources**: Combine multiple inventory types within the same testing scenario
- **Multi-source patterns**: Separate infrastructure provider inventory from molecule-specific configuration inventory
- **File-based data sharing**: Use temporary files to persist and share host-specific data between actions

**Native inventory workflow patterns**
Teams can configure Molecule to use external inventory sources by leveraging the `ansible.executor.args.ansible_playbook` configuration to pass inventory parameters directly to `ansible-playbook`. Targeting can be achieved either through `--limit` flags at the molecule level or through `hosts:` directives at the individual playbook level:

```yaml
# Using external static inventory directory
ansible:
  executor:
    args:
      ansible_playbook:
        - --inventory=${% raw %}{MOLECULE_SCENARIO_DIRECTORY}{% endraw %}/inventory/

# Using cloud inventory plugin
ansible:
  executor:
    args:
      ansible_playbook:
        - --inventory=aws_ec2.yml

# Using existing enterprise inventory with selective targeting
ansible:
  executor:
    args:
      ansible_playbook:
        - --inventory=/path/to/enterprise/inventory/
        - --limit=staging_environment

# Using multiple inventory sources
ansible:
  executor:
    args:
      ansible_playbook:
        - --inventory=static_hosts.yml
        - --inventory=dynamic_script.py
        - --inventory=constructed_groups.yml

# Combining infrastructure provider inventory with molecule-specific configuration
ansible:
  executor:
    args:
      ansible_playbook:
        - --inventory=aws_ec2.yml              # Cloud provider dynamic inventory
        - --inventory=${% raw %}{MOLECULE_SCENARIO_DIRECTORY}{% endraw %}/molecule_config.yml  # Molecule-specific config

# Using inventory from parent directory (shared across scenarios)
ansible:
  executor:
    args:
      ansible_playbook:
        - --inventory=../shared_inventory/

# Alternative: Using ansible.cfg for inventory configuration
ansible:
  cfg:
    defaults:
      host_key_checking: false
      inventory: ../shared_inventory/
  executor:
    args:
      ansible_playbook:
        - --limit=staging_environment
```

### Benefits of native inventory integration

- **Single source of truth**: Reuse existing inventory definitions that contain both production and lab/staging/test systems, eliminating inventory duplication and ensuring consistency across environments
- **Production parity**: Test using the same inventory systems and patterns as production deployments while targeting appropriate lab or staging systems, ensuring that test environments accurately reflect real-world usage patterns
- **Selective targeting**: Use Ansible's `--limit` functionality with existing inventory to target specific environments (lab, staging) without duplicating inventory definitions
- **Existing resource utilization**: Leverage already-provisioned infrastructure for testing without requiring Molecule to manage resource lifecycles
- **Inventory validation**: Test inventory plugins, dynamic scripts, and constructed configurations as part of the automation testing process
- **Enterprise integration**: Use existing CMDB, monitoring, or asset management systems as inventory sources for comprehensive testing
- **Multi-source flexibility**: Combine infrastructure provider inventory (cloud/hyperscaler) with molecule-specific configuration inventory for separation of concerns
- **Multi-action data sharing**: Use simple file-based patterns to share host-specific data between create, converge, verify, and destroy actions
- **Multi-environment testing**: Test automation against development, lab, and staging systems from the same inventory source using different targeting strategies
- **Reduced complexity**: Eliminate the need for complex inventory generation and focus on testing automation logic against realistic inventory structures

**Single source of truth patterns**
A key advantage of native inventory integration is the ability to reuse existing inventory definitions that already contain multiple environments, eliminating the need to duplicate or manage inventory within the testing suite:

```yaml
# Example: Existing enterprise inventory structure
# /opt/ansible/inventory/hosts.yml
all:
  children:
    web_servers:
      children:
        web_production:
          hosts:
            web-prod-01: { environment: production }
            web-prod-02: { environment: production }
        web_staging:
          hosts:
            web-stage-01: { environment: staging }
            web-stage-02: { environment: staging }
        web_lab:
          hosts:
            web-lab-01: { environment: lab }
            web-lab-02: { environment: lab }

# Molecule scenarios using the same inventory with selective targeting
# scenario1/molecule.yml - Test against staging systems
ansible:
  executor:
    args:
      ansible_playbook:
        - --inventory=/opt/ansible/inventory/
        - --limit=web_staging

# scenario2/molecule.yml - Test against lab systems
ansible:
  executor:
    args:
      ansible_playbook:
        - --inventory=/opt/ansible/inventory/
        - --limit=web_lab

# scenario3/molecule.yml - Test against specific environment
ansible:
  executor:
    args:
      ansible_playbook:
        - --inventory=/opt/ansible/inventory/
        - --limit=environment_staging
```

**Alternative targeting approaches**
Beyond using `--limit` at the molecule level, teams can also target specific groups directly in playbooks using Ansible's `hosts:` directive:

```yaml
# create.yml - Target only staging web servers
---
- name: Create staging web infrastructure
  hosts: web_staging
  gather_facts: false
  tasks:
    - name: Provision staging web servers
      # provisioning tasks here

# converge.yml - Target lab database servers
---
- name: Configure lab databases
  hosts: database_lab
  gather_facts: false
  tasks:
    - name: Configure database settings
      # configuration tasks here

# verify.yml - Target specific environment group
---
- name: Verify test environment
  hosts: environment_test
  gather_facts: false
  tasks:
    - name: Run verification tests
      # verification tasks here
```

This approach ensures:

- **Consistency**: Same inventory structure across all environments
- **No duplication**: Single inventory source maintained by operations teams
- **Selective targeting**: Choose between `--limit` flags or playbook `hosts:` directives
- **Flexible targeting**: Mix and match targeting approaches within the same scenario
- **Action-level control**: Different playbooks can target different groups from the same inventory
- **Production alignment**: Test scenarios use identical inventory patterns as production deployments

**Multi-source inventory patterns**
A powerful approach involves combining enterprise infrastructure configuration inventory with molecule-specific test instance definitions. This pattern separates concerns: the infrastructure inventory provides enterprise-level AWS configuration (VPCs, subnets, security groups, required tags), while the molecule inventory defines the specific test instances to be created using that infrastructure:

```yaml
# Example: AWS enterprise infrastructure + Molecule test instances
# molecule.yml
ansible:
  executor:
    args:
      ansible_playbook:
        - --inventory=aws_infrastructure.yml         # Enterprise AWS infrastructure config
        - --inventory=${% raw %}{MOLECULE_SCENARIO_DIRECTORY}{% endraw %}/molecule_config.yml  # Test instances to create

# aws_infrastructure.yml (enterprise infrastructure configuration)
all:
  vars:
    aws_secret: "{% raw %}{{ vault_aws_secret }}{% endraw %}"

# molecule_config.yml (molecule-specific test instances and configuration)
all:
  vars:
    ansible_user: ubuntu
  children:
    web_servers:
      hosts:
        web-test-01:
          instance_type: t3.small
```

This multi-source approach provides:

- **Separation of concerns**: Enterprise infrastructure configuration vs. test instance definitions
- **Secure credential management**: Use Ansible Vault for sensitive AWS credentials and test secrets
- **Enterprise compliance**: Ensure all test instances use required tags, security groups, and compliance settings
- **Infrastructure reuse**: Leverage existing enterprise VPCs, subnets, and security configurations for testing
- **Provider agnostic**: Works with any cloud provider or infrastructure management system
- **Consistent provisioning**: All test instances follow enterprise standards and governance policies
- **Reduced maintenance**: Infrastructure team manages enterprise config, testing team manages test instances
- **Environment flexibility**: Same enterprise configuration works across different testing scenarios and regions

This pattern directly demonstrates several [testing framework requirements](#essential-functionality-requirements):

- **Configuration adaptability**: Supporting diverse infrastructure patterns and enterprise integration requirements
- **Variable and secret management**: Secure handling of enterprise credentials while maintaining test-specific configurations
- **Multi-platform support**: Abstract enterprise infrastructure complexity while enabling test-specific instance definitions
- **Extensibility and integration**: Clean integration with existing enterprise toolchains and governance policies

**Multi-scenario/multi-action data sharing**
When using native inventory patterns, teams often need to share host-specific data between different Molecule actions (create, converge, verify, destroy). This is especially valuable when using `--shared-state`, where the `default` scenario's create action provisions infrastructure and other scenarios need access to resource-specific data captured during that initial provisioning. A simple and effective approach uses temporary files to pass data from one action to subsequent actions:

```yaml
# Example: Sharing infrastructure and host-specific data between actions
# default/create.yml - Generate shared infrastructure and host-specific data during provisioning
---
- name: Store infrastructure and host-specific data for other scenarios
  hosts: localhost
  gather_facts: false
  vars:
    execution_vars: "{% raw %}{{ molecule_ephemeral_directory }}{% endraw %}/execution_vars/"
  tasks:
    - name: Ensure execution vars directory exists
      ansible.builtin.file:
        path: "{% raw %}{{ execution_vars }}{% endraw %}"
        state: directory
        mode: "0755"

    - name: Capture build details
      ansible.builtin.command: echo "Initializing host {% raw %}{{ item }}{% endraw %} at {% raw %}{{ ansible_date_time.iso8601 }}{% endraw %}"
      loop: "{% raw %}{{ groups['molecule'] }}{% endraw %}"
      register: results

    - name: Write host-specific data files for each molecule host
      ansible.builtin.copy:
        dest: "{% raw %}{{ execution_vars }}{% endraw %}host_{% raw %}{{ item.item }}{% endraw %}.yml"
        content: "{% raw %}{{ data | to_yaml }}{% endraw %}"
        mode: "0644"
      vars:
        data:
          host_specific_value: "{% raw %}{{ item.stdout }}{% endraw %}"
      loop: "{% raw %}{{ results.results }}{% endraw %}"

# other-scenario/converge.yml - Load host-specific data
---
- name: Configure applications with host-specific data
  hosts: molecule
  gather_facts: false
  vars:
    execution_vars: "{% raw %}{{ molecule_ephemeral_directory }}{% endraw %}/execution_vars/"
  vars_files:
    - "{% raw %}{{ execution_vars }}{% endraw %}host_{% raw %}{{ inventory_hostname }}{% endraw %}.yml"
  tasks:
    - name: Display host-specific data unique to this host
      ansible.builtin.debug:
        msg: "Host-specific value: {% raw %}{{ host_specific_value }}{% endraw %}"

# default/destroy.yml - Clean up temp files after instances are destroyed
---
- name: Final cleanup of host-specific data
  hosts: localhost
  gather_facts: false
  vars:
    execution_vars: "{% raw %}{{ molecule_ephemeral_directory }}{% endraw %}/execution_vars/"
  tasks:
    - name: Destroying resources
      ansible.builtin.debug:
        msg: "Tearing down infrastructure for host: {% raw %}{{ item }}{% endraw %}"
      loop: "{% raw %}{{ groups['molecule'] }}{% endraw %}"

    - name: Remove execution vars directory
      ansible.builtin.file:
        path: "{% raw %}{{ execution_vars }}{% endraw %}"
        state: absent
        recurse: true
      ignore_errors: true
```

This multi-action data sharing approach provides:

- **Cross-action data persistence**: Enable `create` action on localhost to share captured data with subsequent actions on target hosts
- **Localhost-to-host data flow**: Demonstrate how localhost operations can provide data for individual host operations
- **File-based state sharing**: Use ephemeral directory files to bridge the gap between separate ansible-playbook executions
- **Per-host data isolation**: Each host gets its own data file while sharing the same capture mechanism
- **Action independence**: Each action can independently access host-specific data from previous actions without complex delegation
- **Simple cleanup**: Single directory removal cleans up all execution data files efficiently

**Advanced inventory patterns**
Native inventory support enables sophisticated testing patterns that mirror production deployment workflows:

```yaml
# Testing with constructed inventory for dynamic grouping
# inventory/01-static.yml
all:
  hosts:
    web-01: { role: web, environment: lab }
    web-02: { role: web, environment: staging }
    db-01: { role: database, environment: lab }

# inventory/02-constructed.yml
plugin: ansible.builtin.constructed
strict: false
groups:
  web_servers: role == 'web'
  databases: role == 'database'
  lab: environment == 'lab'
  staging: environment == 'staging'

# Molecule configuration using this inventory
ansible:
  executor:
    args:
      ansible_playbook:
        - --inventory=${% raw %}{MOLECULE_SCENARIO_DIRECTORY}{% endraw %}/inventory/
```

**Cross-scenario inventory coordination**
For testing scenarios that require coordination between multiple test runs, teams can use shared inventory directories that multiple scenarios reference:

```bash
project/
├── molecule/
│   ├── inventory/                # Shared inventory directory
│   │   ├── hosts.yml
│   │   ├── constructed.yml
│   │   └── group_vars/
│   ├── infrastructure/
│   │   └── molecule.yml         # Points to ../inventory/
│   ├── application/
│   │   └── molecule.yml         # Points to ../inventory/
│   └── integration/
│       └── molecule.yml         # Points to ../inventory/
```

This approach provides inventory coordination benefits while maintaining standard Ansible inventory patterns and eliminating dependency on Molecule-specific inventory management features.

**Testing strategy considerations**
Teams must balance isolation, resource efficiency, and test reliability when designing their testing approach. Native inventory support enables flexible strategies that can be tailored to specific requirements:

**Complete isolation scenarios (recommended for):**

- **Independent feature testing**: Each test scenario uses separate inventory and infrastructure to avoid interference
- **Unit testing**: Fast, focused tests that validate specific automation logic against isolated resources
- **Regression testing**: Ensuring new changes don't break existing functionality in clean environments
- **CI/CD pipelines**: Parallel test execution where isolation prevents race conditions and resource conflicts
- **Development workflows**: Individual developers use isolated environments for experimentation and iteration

**Resource sharing scenarios (recommended for):**

- **Integration testing**: Multiple scenarios test against the same infrastructure using shared inventory sources
- **Performance testing**: Establishing baselines and measuring changes over time against consistent environments
- **Cost-sensitive environments**: Cloud testing where infrastructure costs are significant and resource reuse is beneficial
- **Long-running test suites**: Complex scenarios where infrastructure setup time exceeds test execution time
- **Production parity testing**: Testing against existing lab or staging inventory sources that mirror production patterns

**Implementation strategies**
Native inventory support enables various approaches to resource management and test isolation:

```bash
# Complete isolation - each scenario manages its own resources
molecule test --scenario-name feature-test --report --command-borders
# Uses scenario-specific inventory and infrastructure

# Shared inventory coordination - multiple scenarios use common inventory
molecule test --scenario-name infrastructure-test --report --command-borders  # Uses ../shared_inventory/
molecule test --scenario-name application-test --report --command-borders     # Uses ../shared_inventory/
molecule test --scenario-name integration-test --report --command-borders     # Uses ../shared_inventory/

# External inventory testing - test against existing systems
molecule test --scenario-name staging-validation --report --command-borders   # Uses --inventory=staging_hosts.yml
molecule test --scenario-name lab-verification --report --command-borders     # Uses --inventory=lab_inventory.py

# Single source of truth with selective targeting
molecule test --scenario-name web-staging --report --command-borders          # Uses enterprise inventory --limit=web_staging
molecule test --scenario-name db-lab --report --command-borders               # Uses enterprise inventory --limit=database_lab
molecule test --scenario-name app-test --report --command-borders             # Uses enterprise inventory --limit=environment_test

# Playbook-level targeting (no --limit needed)
molecule test --scenario-name staging-deployment --report --command-borders   # Playbooks use hosts: web_staging, hosts: db_staging
molecule test --scenario-name lab-testing --report --command-borders          # Playbooks use hosts: lab_environment
molecule test --scenario-name multi-tier --report --command-borders           # Different actions target different groups

# Multi-source inventory patterns
molecule test --scenario-name cloud-discovery --report --command-borders      # Uses cloud inventory + molecule config
molecule test --scenario-name hybrid-infrastructure --report --command-borders # Uses multiple provider inventories + test config
molecule test --scenario-name dynamic-targeting --report --command-borders    # Cloud provider discovers, molecule configures

# Multi-action data sharing patterns
molecule test --scenario-name host-specific-data --report --command-borders   # Uses file-based vars sharing between actions
molecule test --scenario-name secret-propagation --report --command-borders   # Shares secrets from create to converge/verify
molecule test --scenario-name dynamic-configuration --report --command-borders # Generates host configs in create, uses in other actions

# Shared-state with data propagation
molecule test --all --shared-state --report --command-borders                 # Default creates infrastructure, other scenarios use shared data
molecule test --scenario-name app-deploy --shared-state --report --command-borders    # Uses infrastructure data from default scenario
molecule test --scenario-name integration --shared-state --report --command-borders   # Accesses database/LB endpoints from default

# Mixed approach for comprehensive testing
molecule test --scenario-name isolated-unit --report --command-borders        # Isolated resources
molecule test --scenario-name shared-integration --report --command-borders   # Shared inventory
molecule test --scenario-name lab-validation --report --command-borders       # External inventory
```

This flexibility allows teams to optimize their testing strategies based on resource constraints, execution time requirements, and test isolation needs while maintaining the reliability and reproducibility essential for effective automation testing through native Ansible inventory integration.

### Configuration flexibility and extensibility

**Using Ansible as the default driver**
Molecule leverages Ansible as its default driver, providing significant benefits for automation testing across all domains. This approach enables teams to use the same Ansible knowledge, playbooks, and patterns for both test environment management and production automation. By using Ansible's declarative syntax for infrastructure provisioning, application deployment, and service configuration, teams maintain consistency between test environments and production patterns. This reduces learning curves, improves test reliability through familiar constructs, and ensures that test scenarios closely mirror real-world automation usage regardless of the target domain.

**Dependency management integration**
Molecule integrates with Ansible Galaxy for dependency resolution, ensuring that test environments include all required roles and collections regardless of their domain focus. Whether testing infrastructure automation, application deployment, network configuration, or external service integration, this integration supports both public and private repositories while handling version constraints and conflict resolution across all types of Ansible content.

**Using Ansible as provisioner and verifier**
Molecule uses Ansible as both the provisioner and verifier, providing unified automation execution and validation logic across all testing scenarios. This approach ensures that teams use the same Ansible skills, modules, and patterns for both test execution and validation that they use in production automation. Whether provisioning infrastructure, deploying applications, configuring services, or validating outcomes, Ansible's extensive module ecosystem provides consistent interfaces for all automation domains. This unified approach reduces complexity, leverages existing team expertise, and ensures that test validation logic can be easily understood and maintained by any team member familiar with Ansible.

### Resource lifecycle optimization

**Efficient environment provisioning**
Molecule optimizes test environment creation through template reuse, incremental updates, and parallel provisioning where supported by the underlying platform. These optimizations work across all automation domains: infrastructure resources, application instances, database configurations, and external service setups. The framework reduces test execution time while maintaining isolation guarantees regardless of whether you're testing infrastructure provisioning, application deployment, or complex integration scenarios.

**Intelligent cleanup strategies**
The framework provides multiple cleanup strategies, from complete teardown to selective resource removal across all automation domains. This flexibility supports both cost optimization (cleaning up expensive cloud resources) and debugging workflows where preserving failed environments aids troubleshooting (maintaining application logs, database states, or external service configurations for post-test analysis).

**Integration with automation as code**
Molecule's approach aligns naturally with automation as code principles, treating test environments as versioned, repeatable, and auditable across all domains. Whether managing infrastructure, applications, integrations, or business processes, this alignment ensures that testing practices support broader automation maturity goals and DevOps transformation initiatives.

Through this comprehensive approach, Molecule transforms Ansible testing from an ad-hoc activity into a structured, repeatable practice that scales from individual development through enterprise deployment pipelines. The framework's design acknowledges that effective testing must balance thoroughness with practicality across all automation domains, providing the tools teams need to implement testing strategies that actually get used regardless of whether they're automating infrastructure, applications, integrations, or complex business processes.

## Molecule's evolution with Ansible

As Ansible has emerged as the de facto DSL for automation, Molecule's development continues with deeper Ansible integration as the primary focus. Rather than broadening tool support, Molecule's evolution prioritizes making the Molecule + Ansible experience seamless, intuitive, and powerful while maintaining backward compatibility for existing workflows.

### Current and planned integration enhancements

**Enhanced collection testing support**
Molecule's native inventory integration capabilities provide comprehensive support for Ansible collection testing scenarios. This includes automatic collection detection to streamline testing workflows, improved collection dependency resolution, and optimized testing patterns that reflect how collections are developed and deployed in enterprise environments using existing inventory systems.

**Unified user experience**
Visual and functional alignment with Ansible's output patterns ensures that teams experience consistent interfaces across their automation toolkit. This includes UI changes that better integrate Molecule's test output with standard Ansible playbook output, making the transition between development, testing, and deployment workflows more natural and reducing cognitive overhead for automation practitioners.

**Deeper inventory integration**
More obvious and tighter integration with Ansible's inventory systems eliminates friction between test and production inventory patterns. This includes comprehensive native support for external inventory sources (static files, dynamic scripts, and inventory plugins), improved inventory validation during testing, and clearer mapping between test inventory structures and production deployment patterns. Teams can seamlessly test automation using production inventory patterns against appropriate lab and staging systems while maintaining flexibility for cross-scenario coordination through standard Ansible inventory patterns.

**Extended executor support**
Support for modern Ansible execution environments through tools like ansible-navigator enables testing within the same containerized environments used for production automation. This ensures test environments more accurately reflect production execution contexts while supporting the shift toward standardized, reproducible automation execution environments.

**Streamlined automation workflows**
Automatic detection and configuration of Ansible collections, roles, and dependencies reduces manual configuration overhead while ensuring that testing workflows automatically adapt to evolving automation codebases. This includes intelligent detection of collection structures, automatic dependency resolution, and seamless integration with Ansible Galaxy workflows.

### Strategic direction

Molecule's roadmap focuses on becoming the definitive testing solution for Ansible automation rather than a generic testing framework. This specialization enables deeper integration, more intuitive workflows, and better alignment with Ansible ecosystem patterns while ensuring that teams can leverage their existing Ansible expertise throughout their entire testing lifecycle.

The framework's evolution maintains backward compatibility with existing workflows while progressively enhancing the Ansible-native experience, ensuring that teams can adopt new capabilities at their own pace without disrupting established testing practices.
