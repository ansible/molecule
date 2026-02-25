# Configuration

## Prerun

To help Ansible find used modules and roles, molecule will
perform a prerun set of actions. These involve installing dependencies
from `requirements.yml` specified at the project level, installing a standalone
role or a collection. The destination is `project_dir/.cache` and the
code itself was reused from ansible-lint, which has to do the same
actions. (Note: ansible-lint is not included with molecule.)

This assures that when you include a role inside molecule playbooks,
Ansible will be able to find that role and that the include is exactly
the same as the one you are expecting to use in production.

If for some reason the prerun action does not suit your needs, you can
still disable it by adding `prerun: false` inside the
configuration file.

Keep in mind that you can add this value to the
`.config/molecule/config.yml` file, in your `$HOME` or at the root of
your project, in order to avoid adding it to each scenario.

## Role name check

By default, `Molecule` will check whether the role name follows the name
standard. If not, it will raise an error.

If the computed fully qualified role name does not follow current galaxy
requirements, you can ignore it by adding `role_name_check:1` inside the configuration file.

It is strongly recommended to follow the name standard of
[namespace](https://docs.ansible.com/projects/ansible/latest/dev_guide/collections_galaxy_meta.html#structure)
and
[role](https://docs.ansible.com/projects/lint/rules/role-name/#role-name).
A `computed fully qualified role name` may further contain the dot character.

## Shared State

By default, Molecule runs each scenario independently with its own isolated state and resources. When `shared_state` is enabled, scenarios share ephemeral state, allowing them to access resources created by the `default` scenario.

This is particularly useful for multi-scenario testing where one scenario manages testing resource lifecycle while other scenarios perform testing against those resources.

To enable shared state, add `shared_state: true` to your configuration file:

```yaml
---
shared_state: true
# ... rest of configuration
```

**Effects of enabling shared state:**

- All scenarios share the same ephemeral state directory
- The default scenario handles create/destroy actions for all scenarios
- Component scenarios can access resources created by the default scenario
- Scenarios skip their own create/destroy actions when shared resources are managed elsewhere
- Faster execution with single infrastructure lifecycle instead of per-scenario setup/teardown

**Configuration locations:**

You can add this setting to:

- `.config/molecule/config.yml` file in your `$HOME` directory (global default)
- Base `config.yml` file at the project root (project default)
- Collection molecule directory `extensions/molecule/config.yml`
- Individual scenario `molecule.yml` files (scenario-specific override)

**Alternative:** The `--shared-state` command-line flag can also enable this behavior temporarily, but configuration file approach is recommended for consistent usage.

## Variable Substitution

Configuration options may contain environment variables.

```yaml
entry:
  - value: ${ENV_VAR}
```

Molecule will substitute `$ENV_VAR` with the value of the
`ENV_VAR` environment variable.

!!! warning

    If an environment variable is not set, Molecule substitutes with an
    empty string.

Both `$VARIABLE` and `${VARIABLE}` syntax are supported. Extended
shell-style features, such as `${VARIABLE-default}` and
`${VARIABLE:-default}` are also supported. Even the default as another
environment variable is supported like `${VARIABLE-$DEFAULT}` or
`${VARIABLE:-$DEFAULT}`. An empty string is returned when
both variables are undefined.

If a literal dollar sign is needed in a configuration, use a double dollar
sign (`$$`).

Molecule will substitute special `MOLECULE_` environment variables
defined in `molecule.yml`.

!!! note

    Remember, the ``MOLECULE_`` namespace is reserved for Molecule.  Do not
    prefix your own variables with `MOLECULE_`.

A file may be placed in the root of the project as `.env.yml`, and Molecule
will read variables when rendering `molecule.yml`. See command usage.

Following are the environment variables available in `molecule.yml`:

MOLECULE_DEBUG

: If debug is turned on or off

MOLECULE_FILE

: Path to molecule config file, usually
`~/.cache/molecule/<role-name>/<scenario-name>/molecule.yml`

MOLECULE_ENV_FILE

: Path to molecule environment file, usually `<role_path>/.env.yml`

MOLECULE_STATE_FILE

: The path to molecule state file contains the state of the instances
(created, converged, etc.). Usually
`~/.cache/molecule/<role-name>/<scenario-name>/state.yml`

MOLECULE_INVENTORY_FILE

: Path to generated inventory file, usually
`~/.cache/molecule/<role-name>/<scenario-name>/inventory/ansible_inventory.yml`

MOLECULE_EPHEMERAL_DIRECTORY

: Path to generated directory, usually
`~/.cache/molecule/<role-name>/<scenario-name>`

MOLECULE_SCENARIO_DIRECTORY

: Path to scenario directory, usually
`<role_path>/molecule/<scenario-name>`

MOLECULE_PROJECT_DIRECTORY

: Path to your project (role) directory, usually `<role_path>`

MOLECULE_INSTANCE_CONFIG

: Path to the instance config file, contains instance name,
connection, user, port, etc. (populated from driver). Usually
`~/.cache/molecule/<role-name>/<scenario-name>/instance_config.yml`

MOLECULE_ANSIBLE_ARGS_STRICT_MODE

: When set to any non-empty value, reverts to legacy behavior where `ansible_args`
are excluded from create and destroy actions regardless of playbook source.
By default (unset), `ansible_args` are included for user-provided create/destroy
playbooks but excluded for bundled playbooks for safety.

MOLECULE_DEPENDENCY_NAME

: Dependency type name, usually 'galaxy'

MOLECULE_SCENARIO_NAME

: Name of the scenario

MOLECULE_VERBOSITY

: Determine Ansible verbosity level.

!!! note

    The following environment variables exist for pre ansible-native use and should not
    be used when using an ansible-native configuration.

MOLECULE_DRIVER_NAME

: Name of the molecule scenario driver

MOLECULE_PROVISIONER_NAME

: Name of the provisioner tool (usually 'ansible')

MOLECULE_VERIFIER_NAME

: Name of the verifier tool (usually 'ansible')

MOLECULE_VERIFIER_TEST_DIRECTORY

: Path of the directory that contains verifier tests, usually
`<role_path>/<scenario-name>/<verifier-name>`

## Dependency

Testing content may rely upon additional dependencies. Molecule handles
managing these dependencies by invoking configurable dependency
managers.

### Ansible Galaxy

[DEFAULT_ROLES_PATH]: https://docs.ansible.com/projects/ansible/latest/cli/ansible-galaxy.html#cmdoption-ansible-galaxy-role-remove-p
[ANSIBLE_HOME]: https://docs.ansible.com/projects/ansible/latest/reference_appendices/config.html#ansible-home

Galaxy is the default dependency manager.

From v6.0.0, the dependencies are installed in the directory that defined
in ansible configuration. The default installation directory is
[DEFAULT_ROLES_PATH][]([ANSIBLE_HOME][]). If two versions of the same
dependency is required, there is a conflict if the default installation
directory is used because both are tried to be installed in one directory.

Additional options can be passed to `ansible-galaxy install` through the
options dict. Any option set in this section will override the defaults.

The `role-file` and `requirements-file` search path is `<role-name>`
directory. The default value for `role-file` is `requirements.yml`, and the
default value for `requirements-file` is `collections.yml`.

1. If they are not defined in `options`, `molecule` will find them from the
   `<role-name>` directory, e.g. `<role-name>/requirements.yml` and
   `<role-name>/collections.yml`
2. If they are defined in `options`, `molecule` will find them from
   `<role-name>/<the-value-of-role-file>` and
   `<role-name>/<the-value-of-requirements-file>`.

!!! note

    Molecule will remove any options matching '^[v]+$', and pass ``-vvv``
    to the underlying ``ansible-galaxy`` command when executing
    `molecule --debug`.

```yaml
dependency:
  name: galaxy
  options:
    ignore-certs: True
    ignore-errors: True
    role-file: requirements.yml
    requirements-file: collections.yml
```

Use "role-file" if you have roles only. Use the "requirements-file" if you
need to install collections. Note that, with Ansible Galaxy's collections
support, you can now combine the two lists into a single requirement if your
file looks like this

```yaml
roles:
  - dep.role1
  - dep.role2
collections:
  - ns.collection
  - ns2.collection2
```

If you want to combine them, then just point your `role-file` and
`requirements-file` to the same path. This is not done by default because
older `role-file` only required a list of roles, while the collections
must be under the `collections:` key within the file and pointing both to
the same file by default could break existing code.

The dependency manager can be disabled by setting `enabled` to False.

```yaml
dependency:
  name: galaxy
  enabled: False
```

Environment variables can be passed to the dependency.

```yaml
dependency:
  name: galaxy
  env:
    FOO: bar
```

### Shell

`Shell` is an alternate dependency manager.

It is intended to run a command in situations where `Ansible Galaxy`\_
don't suffice.

The `command` to execute is required, and is relative to Molecule's
project directory when referencing a script not in $PATH.

!!! note

    Unlike the other dependency managers, ``options`` are ignored and not
    passed to `shell`.  Additional flags/subcommands should simply be added
    to the `command`.

```yaml
dependency:
  name: shell
  command: path/to/command --flag1 subcommand --flag2
```

The dependency manager can be disabled by setting `enabled` to False.

```yaml
dependency:
  name: shell
  command: path/to/command --flag1 subcommand --flag2
  enabled: False
```

Environment variables can be passed to the dependency.

```yaml
dependency:
  name: shell
  command: path/to/command --flag1 subcommand --flag2
  env:
    FOO: bar
```

## Scenario

Molecule treats scenarios as a first-class citizens, with a top-level
configuration syntax.

A scenario allows Molecule to test a role in a particular way, this is a
fundamental change from Molecule v1.

A scenario is a self-contained directory containing everything necessary
for testing the role in a particular way. The default scenario is named
`default`, and every role should contain a default scenario.

Unless mentioned explicitly, the scenario name will be the directory name
hosting the files.

Any option set in this section will override the defaults.

```yaml
scenario:
  create_sequence:
    - dependency
    - create
    - prepare
  check_sequence:
    - dependency
    - cleanup
    - destroy
    - create
    - prepare
    - converge
    - check
    - destroy
  converge_sequence:
    - dependency
    - create
    - prepare
    - converge
  destroy_sequence:
    - dependency
    - cleanup
    - destroy
  test_sequence:
    - dependency
    - cleanup
    - destroy
    - syntax
    - create
    - prepare
    - converge
    - idempotence
    - side_effect
    - verify
    - cleanup
    - destroy
```

### Nested Scenarios (Collections)

When testing Ansible collections with many components, a flat scenario layout
can become difficult to navigate. For example, a collection with 48 resource
modules and 4 states each would produce ~200 flat directories under
`extensions/molecule/`.

Molecule supports **nested scenario directories** in collection mode, allowing
you to group related scenarios under a parent directory:

```text
extensions/molecule/
├── config.yml
├── default/
│   └── molecule.yml
├── appliance_vlans/
│   ├── merged/
│   │   └── molecule.yml
│   ├── replaced/
│   │   └── molecule.yml
│   └── deleted/
│       └── molecule.yml
├── wireless_ssid/
│   ├── merged/
│   │   └── molecule.yml
│   └── replaced/
│       └── molecule.yml
```

#### Targeting nested scenarios

Use a `/` in the `-s` flag to target nested scenarios:

```bash
molecule test -s appliance_vlans/merged
molecule test -s appliance_vlans/replaced
molecule test -s wireless_ssid/merged
```

You can also use wildcards to target all scenarios under a group:

```bash
molecule test -s "appliance_vlans/*"
```

Flat scenarios continue to work exactly as before:

```bash
molecule test -s default
```

No changes to `molecule.yml` files are required. The directory path relative
to the collection molecule root (`extensions/molecule/`) becomes the scenario
name automatically.

#### Discovery

To discover nested scenarios with `molecule list` or `molecule test --all`,
set `MOLECULE_GLOB` to a recursive pattern:

```bash
export MOLECULE_GLOB="extensions/molecule/**/molecule.yml"
```

This finds `molecule.yml` files at any depth under `extensions/molecule/`.

#### Scenario naming

In collection mode, Molecule derives the scenario name from the relative path
between `extensions/molecule/` and the directory containing `molecule.yml`:

| Directory                                          | Scenario name             |
|----------------------------------------------------|---------------------------|
| `extensions/molecule/default/`                     | `default`                 |
| `extensions/molecule/appliance_vlans/merged/`      | `appliance_vlans/merged`  |
| `extensions/molecule/appliance_vlans/replaced/`    | `appliance_vlans/replaced`|

The name shown by `molecule list` is exactly what you pass to `-s`, giving
round-trip consistency. Role-mode scenarios (under `molecule/`) are unaffected
and continue to use the directory basename.

!!! note

    Nested scenario support is only available in collection mode
    (projects with `extensions/molecule/`). Standard role-mode testing
    is unchanged.

## Advanced testing

If needed, Molecule can run multiple side effects and tests within a scenario.
This allows to perform advanced testing for stateful software under role/playbook
management. Actions `side_effect` and `verify` can take optional arguments to change
the playbook/test they execute.

Example of test sequence with multiple side effects and tests:

```yaml
test_sequence:
  - converge
  - side_effect reboot.yaml
  - verify after_reboot/
  - side_effect alter_configs.yaml
  - converge
  - verify other_test1.py other_test2.py
  - side_effect
  - verify
```

`side_effect` without an argument is executing the usual `side_effect` configured in
`provisioner.playbooks` section of molecule.yml.

`side_effect` can have one or more arguments (separated by spaces) which is
a playbook (playbooks) to execute. If the argument for `side_effect` is present,
it's executed instead. The path to the playbook is relative to the molecule.yml location.
Normal side effect settings (from `provisioner.playbooks`) are ignored for action with
argument.

`verify` without an argument is executing the usual tests configured in the verifier section
of molecule.yml.

If one or more arguments (separated by spaces) are present, each argument is treated
as a test name (file or directory) to pass to the verifier (either Ansible or Testinfra).
The kind of verifier is set in the `verifier` section of molecule.yml and is applied to all
`verify` actions in the scenario.

The path to tests is relative to the molecule.yml file location. The `additional_files_or_dirs`
setting for the verifier is ignored if the `verify` action is provided with an argument.

Multiple `side_effect` and `verify` actions can be used to create a combination
of playbooks and tests, for example, for end-to-end playbook testing.

Additional `converge` and `idempotence` actions can be used multiple times:

```yaml
test_sequence:
  - converge
  - idempotence
  - side_effect
  - verify
  - converge
  - idempotence
  - side_effect effect2.yml
  - converge
  - idempotence
  - verify test2/
  - side_effect effect3.yml
  - verify test3/
  - idempotence
```

## Driver (pre ansible-native)

!!! note

    **Driver** is pre ansible-native construct. It is not necessary
    when using an ansible-native configuration.
    For details see [ansible-native](ansible-native.md).

Molecule uses Ansible to manage instances to operate on.
Molecule supports any provider Ansible supports. This work
is offloaded to the `provisioner`.

The driver's name is specified in `molecule.yml`, and can
be overridden on the command line. Molecule will remember the last
successful driver used, and continue to use the driver for all
subsequent subcommands, or until the instances are destroyed by
Molecule.

!!! warning

    The verifier must support the Ansible provider for proper Molecule
    integration.

    The driver's python package requires installation.

### Delegated

Delegated is the default driver used in Molecule.

Under this driver, it is the developers responsibility to implement the
create and destroy playbooks. `Managed` is the default behavior of all
drivers.

```yaml
driver:
  name: de
```

However, the developer must adhere to the instance-config API. The
developer's create playbook must provide the following instance-config
data, and the developer's destroy playbook must reset the instance-config.

```yaml
- address: ssh_endpoint
  identity_file: ssh_identity_file # mutually exclusive with password
  instance: instance_name
  port: ssh_port_as_string
  user: ssh_user
  shell_type: sh
  password: ssh_password # mutually exclusive with identity_file
  become_method: valid_ansible_become_method # optional
  become_pass: password_if_required # optional

- address: winrm_endpoint
  instance: instance_name
  connection: "winrm"
  port: winrm_port_as_string
  user: winrm_user
  password: winrm_password
  shell_type: powershell
  winrm_transport: ntlm/credssp/kerberos
  winrm_cert_pem: <path to the credssp public certificate key>
  winrm_cert_key_pem: <path to the credssp private certificate key>
  winrm_server_cert_validation: validate/ignore
```

This article covers how to configure and use WinRM with Ansible:
<https://docs.ansible.com/projects/ansible/latest/user_guide/windows_winrm.html>

Molecule can also skip the provisioning/deprovisioning steps. It is the
developers responsibility to manage the instances, and properly configure
Molecule to connect to said instances.

```yaml
driver:
  name: default
  options:
    managed: False
    login_cmd_template: "docker exec -ti {instance} bash"
    ansible_connection_options:
      ansible_connection: docker
platforms:
  - name: instance-docker
```

```bash
    $ docker run \
        -d \
        --name instance-docker \
        --hostname instance-docker \
        -it molecule_local/ubuntu:latest sleep infinity & wait
```

Use Molecule with delegated instances, which are accessible over ssh.

!!! note

    It is the developer's responsibility to configure the ssh config file.

```yaml
driver:
  name: default
  options:
    managed: False
    login_cmd_template: "ssh {instance} -F /tmp/ssh-config"
    ansible_connection_options:
      ansible_connection: ssh
      ansible_ssh_common_args: "-F /path/to/ssh-config"
platforms:
  - name: instance
```

Provide the files Molecule will preserve post `destroy` action.

```yaml
driver:
  name: default
  safe_files:
    - foo
```

And in order to use localhost as molecule's target:

```yaml
driver:
  name: default
  options:
    managed: False
    ansible_connection_options:
      ansible_connection: local
```

### Platforms (pre-ansible-native)

!!! note

    **Platforms** is a pre ansible-native construct. It is not necessary
    when using an ansible-native configuration.
    For details see [ansible-native](ansible-native.md)

Platforms define the instances to be tested, and the groups to which the instances belong.

```yaml
platforms:
  - name: instance-1
```

Multiple instances can be provided.

```yaml
platforms:
  - name: instance-1
  - name: instance-2
```

Mapping instances to groups. These groups will be used by the Provisioner\_
for orchestration purposes.

```yaml
platforms:
  - name: instance-1
    groups:
      - group1
      - group2
```

Children allow the creation of groups of groups.

```yaml
platforms:
  - name: instance-1
    groups:
      - group1
      - group2
    children:
      - child_group1
```

## Provisioner (pre ansible-native)

!!! note

    **Provisioner** is a pre ansible-native construct. It is not necessary
    when using an ansible-native configuration.
    For details see [ansible-native](ansible-native.md)

Molecule handles provisioning and converging the role.

### Ansible

Ansible` is the default provisioner. No other provisioner will be supported.

Molecule's provisioner manages the instances lifecycle. However, the user
must provide the create, destroy, and converge playbooks. Molecule's
`init` subcommand will provide the necessary files for convenience.

Molecule will skip tasks which are tagged with either `molecule-notest` or
`notest`. With the tag `molecule-idempotence-notest` tasks are only
skipped during the idempotence action step.

!!! warning

    Reserve the create and destroy playbooks for provisioning.  Do not
    attempt to gather facts or perform operations on the provisioned nodes
    inside these playbooks.  Due to the gymnastics necessary to sync state
    between Ansible and Molecule, it is best to perform these tasks in the
    prepare or converge playbooks.

    It is the developers responsibility to properly map the modules' fact
    data into the instance_conf_dict fact in the create playbook.  This
    allows Molecule to properly configure Ansible inventory.

Additional options can be passed to `ansible-playbook` through the options
dict. Any option set in this section will override the defaults.

!!! note

    Options do not affect the create and destroy actions.

!!! note

    Molecule will remove any options matching `^[v]+$`, and pass ``-vvv``
    to the underlying ``ansible-playbook`` command when executing
    `molecule --debug`.

Molecule will silence log output, unless invoked with the `--debug` flag.
However, this results in quite a bit of output. To enable Ansible log
output, add the following to the `provisioner` section of `molecule.yml`.

```yaml
provisioner:
  name: ansible
  log: True
```

The create/destroy playbooks for Docker and Podman are bundled with
Molecule. These playbooks have a clean API from `molecule.yml`, and
are the most commonly used. The bundled playbooks can still be overridden.

The playbook loading order is:

1. provisioner.playbooks.$driver_name.$action
2. provisioner.playbooks.$action
3. bundled_playbook.$driver_name.$action

```yaml
provisioner:
  name: ansible
  options:
    vvv: True
  playbooks:
    create: create.yml
    converge: converge.yml
    destroy: destroy.yml
```

Share playbooks between roles.

```yaml
provisioner:
  name: ansible
  playbooks:
    create: ../default/create.yml
    destroy: ../default/destroy.yml
    converge: converge.yml
```

Multiple driver playbooks. In some situations a developer may choose to
test the same role against different backends. Molecule will choose driver
specific create/destroy playbooks, if the determined driver has a key in
the playbooks section of the provisioner's dict.

!!! note

    If the determined driver has a key in the playbooks dict, Molecule will
    use this dict to resolve all provisioning playbooks (create/destroy).

```yaml
provisioner:
  name: ansible
  playbooks:
    docker:
      create: create.yml
      destroy: destroy.yml
    create: create.yml
    destroy: destroy.yml
    converge: converge.yml
```

!!! note

    Paths in this section are converted to absolute paths, where the
    relative parent is the $scenario_directory.

The side effect playbook executes actions which produce side effects to the
instances(s). Intended to test HA failover scenarios or the like. It is
not enabled by default. Add the following to the provisioner's `playbooks`
section to enable.

```yaml
provisioner:
  name: ansible
  playbooks:
    side_effect: side_effect.yml
```

!!! note

    This feature should be considered experimental.

The prepare playbook executes actions which bring the system to a given
state prior to converge. It is executed after create, and only once for
the duration of the instances life.

This can be used to bring instances into a particular state, prior to
testing.

```yaml
provisioner:
  name: ansible
  playbooks:
    prepare: prepare.yml
```

The cleanup playbook is for cleaning up test infrastructure that may not
be present on the instance that will be destroyed. The primary use-case
is for "cleaning up" changes that were made outside of Molecule's test
environment. For example, remote database connections or user accounts.
Intended to be used in conjunction with `prepare` to modify external
resources when required.

The cleanup step is executed directly before every destroy step. Just like
the destroy step, it will be run twice. An initial clean before converge
and then a clean before the last destroy step. This means that the cleanup
playbook must handle failures to cleanup resources which have not
been created yet.

Add the following to the provisioner's `playbooks` section
to enable.

```yaml
provisioner:
  name: ansible
  playbooks:
    cleanup: cleanup.yml
```

!!! note

    This feature should be considered experimental.

Environment variables can be passed to the provisioner. Variables in this
section which match the names above will be appended to the above defaults,
and converted to absolute paths, where the relative parent is the
$scenario_directory.

!!! note

    Paths in this section are converted to absolute paths, where the
    relative parent is the $scenario_directory.

```yaml
provisioner:
  name: ansible
  env:
    FOO: bar
```

Modifying ansible.cfg.

```yaml
provisioner:
  name: ansible
  config_options:
    defaults:
      fact_caching: jsonfile
    ssh_connection:
      scp_if_ssh: True
```

!!! note

    The following keys are disallowed to prevent Molecule from
    improperly functioning.  They can be specified through the
    provisioner's env setting described above, with the exception
    of the `privilege_escalation`.

```yaml
provisioner:
  name: ansible
  config_options:
    defaults:
      library: /path/to/library
      filter_plugins: /path/to/filter_plugins
    privilege_escalation: {}
```

Roles which require host/groups to have certain variables set. Molecule
uses the same `variables defined in a playbook`_syntax as `Ansible`_.

```yaml
provisioner:
  name: ansible
  inventory:
    group_vars:
      all:
        bar: foo
      group1:
        foo: bar
      group2:
        foo: bar
        baz:
          qux: zzyzx
    host_vars:
      group1-01:
        foo: baz
```

Molecule automatically generates the inventory based on the hosts defined
under `Platforms`\_. Using the `hosts` key allows to add extra hosts to
the inventory that are not managed by Molecule.

A typical use case is if you want to access some variables from another
host in the inventory (using hostvars) without creating it.

!!! note

    The content of ``hosts`` should follow the YAML based inventory syntax:
    start with the ``all`` group and have hosts/vars/children entries.

```yaml
provisioner:
  name: ansible
  inventory:
    hosts:
      all:
        hosts:
          extra_host:
            foo: hello
```

!!! note

    The extra hosts added to the inventory using this key won't be
    created/destroyed by Molecule. It is the developers responsibility
    to target the proper hosts in the playbook. Only the hosts defined
    under `Platforms`_ should be targeted instead of ``all``.

An alternative to the above is symlinking. Molecule creates symlinks to
the specified directory in the inventory directory. This allows ansible to
converge utilizing its built in host/group_vars resolution. These two
forms of inventory management are mutually exclusive.

Like above, it is possible to pass an additional inventory file
(or even dynamic inventory script), using the `hosts` key. `Ansible`\_ will
automatically merge this inventory with the one generated by molecule.
This can be useful if you want to define extra hosts that are not managed
by Molecule.

!!! note

    Again, it is the developers responsibility to target the proper hosts
    in the playbook. Only the hosts defined under
    `Platforms`_ should be targeted instead of ``all``.

!!! note

    The source directory linking is relative to the scenario's
    directory.

    The only valid keys are ``hosts``, ``group_vars`` and ``host_vars``.  Molecule's
    schema validator will enforce this.

```yaml
provisioner:
  name: ansible
  inventory:
    links:
      hosts: ../../../inventory/hosts
      group_vars: ../../../inventory/group_vars/
      host_vars: ../../../inventory/host_vars/
```

!!! note

    You can use either `hosts`/`group_vars`/`host_vars` sections of inventory OR `links`.
    If you use both, links will win.

```yaml
provisioner:
  name: ansible
  hosts:
    all:
      hosts:
        ignored:
          important: this host is ignored
  inventory:
    links:
      hosts: ../../../inventory/hosts
```

Override connection options:

```yaml
provisioner:
  name: ansible
  connection_options:
    ansible_ssh_user: foo
    ansible_ssh_common_args: -o IdentitiesOnly=no
```

Override tags:

```yaml
provisioner:
name: ansible
config_options:
  tags:
    run: tag1,tag2,tag3
```

A typical use case is if you want to use tags within a scenario.
Don't forget to add a tag `always` in `converge.yml` as below.

```yaml
    ---
    - name: Converge
      hosts: all
      tasks:
        - name: "Include acme.my_role_name"
          ansible.builtin.include_role:
            name: "acme.my_role_name"
          tags:
            - always
```

.. \_`variables defined in a playbook`: <https://docs.ansible.com/projects/ansible/latest/user_guide/playbooks_variables.html#defining-variables-in-a-playbook>

Add arguments to ansible-playbook when running converge:

```yaml
provisioner:
  name: ansible
  ansible_args:
    - --inventory=mygroups.yml
    - --limit=host1,host2
```

## Verifier (pre ansible-native)

!!! note

    **Verifier** is a pre ansible-native construct. It is not necessary
    when using an ansible-native configuration.
    For details see [ansible-native](ansible-native.md).

Molecule handles role testing by invoking configurable verifiers.

### Ansible Verifier

`Ansible`\_ is the default test verifier.

Molecule executes a playbook (`verify.yml`) located in the role's
`scenario.directory`.

```yaml
verifier:
  name: ansible
```

The testing can be disabled by setting `enabled` to False.

```yaml
verifier:
  name: ansible
  enabled: False
```

Environment variables can be passed to the verifier.

```yaml
verifier:
  name: ansible
  env:
    FOO: bar
```

### Testinfra

Testinfra`\_ is no longer the default test verifier since version 3.0.

Additional options can be passed to `testinfra` through the options
dict. Any option set in this section will override the defaults.

!!! note

    Molecule will remove any options matching '^[v]+$', and pass ``-vvv``
    to the underlying ``pytest`` command when executing ``molecule
    --debug``.

```yaml
verifier:
  name: testinfra
  options:
    n: 1
```

The testing can be disabled by setting `enabled` to False.

```yaml
verifier:
  name: testinfra
  enabled: False
```

Environment variables can be passed to the verifier.

```yaml
verifier:
  name: testinfra
  env:
    FOO: bar
```

Change path to the test directory.

```yaml
verifier:
  name: testinfra
  directory: /foo/bar/
```

Additional tests from another file or directory relative to the scenario's
tests directory (supports regexp).

```yaml
verifier:
  name: testinfra
  additional_files_or_dirs:
    - ../path/to/test_1.py
    - ../path/to/test_2.py
    - ../path/to/directory/*
```

.. \_`Testinfra`: <https://testinfra.readthedocs.io>
