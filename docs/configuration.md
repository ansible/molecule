# Configuration

::: molecule.config.Config

## Prerun

In order to help Ansible find used modules and roles, molecule will
perform a prerun set of actions. These involve installing dependencies
from `requirements.yml` specified at project level, install a standalone
role or a collection. The destination is `project_dir/.cache` and the
code itself was reused from ansible-lint, which has to do the same
actions. (Note: ansible-lint is not included with molecule.)

This assures that when you include a role inside molecule playbooks,
Ansible will be able to find that role, and that the include is exactly
the same as the one you are expecting to use in production.

If for some reason the prerun action does not suits your needs, you can
still disable it by adding `prerun: false` inside the
configuration file.

Keep in mind that you can add this value to the
`.config/molecule/config.yml` file, in your `$HOME` or at the root of
your project, in order to avoid adding it to each scenario.

## Role name check

By default, `Molecule` will check whether the role name follows the name
standard. If not, it will raise an error.

If computed fully qualified role name does not follow current galaxy
requirements, you can ignore it by adding `role_name_check:1` inside the configuration file.

It is strongly recommended to follow the name standard of
[namespace](https://galaxy.ansible.com/docs/contributing/namespaces.html#galaxy-namespace-limitations)
and
[role](https://galaxy.ansible.com/docs/contributing/creating_role.html#role-names).

## Variable Substitution

::: molecule.interpolation.Interpolator

There are following environment variables available in `molecule.yml`:

MOLECULE_DEBUG

: If debug is turned on or off

MOLECULE_FILE

: Path to molecule config file, usually
`~/.cache/molecule/<role-name>/<scenario-name>/molecule.yml`

MOLECULE_ENV_FILE

: Path to molecule environment file, usually `<role_path>/.env.yml`

MOLECULE_STATE_FILE

: Path to molecule state file, contains state of the instances
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

MOLECULE_DEPENDENCY_NAME

: Dependency type name, usually 'galaxy'

MOLECULE_DRIVER_NAME

: Name of the molecule scenario driver

MOLECULE_PROVISIONER_NAME

: Name of the provisioner tool (usually 'ansible')

MOLECULE_REPORT

: Name of HTML file where to dump execution report.

MOLECULE_SCENARIO_NAME

: Name of the scenario

MOLECULE_VERBOSITY

: Determine Ansible verbosity level.

MOLECULE_VERIFIER_NAME

: Name of the verifier tool (usually 'ansible')

MOLECULE_VERIFIER_TEST_DIRECTORY

: Path of the directory that contains verifier tests, usually
`<role_path>/<scenario-name>/<verifier-name>`

## Dependency

Testing roles may rely upon additional dependencies. Molecule handles
managing these dependencies by invoking configurable dependency
managers.

### Ansible Galaxy

::: molecule.dependency.ansible_galaxy.AnsibleGalaxy

### Shell

::: molecule.dependency.shell.Shell

## Driver

Molecule uses [Ansible](#ansible-1) to manage instances to operate on.
Molecule supports any provider [Ansible](#ansible-1) supports. This work
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

::: molecule.driver.delegated.Delegated

### Platforms

::: molecule.platforms.Platforms

## Provisioner

Molecule handles provisioning and converging the role.

### Ansible

::: molecule.provisioner.ansible.Ansible

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
a playbook (plabyooks) to execute. If the argument for `side_effect` is present,
it's executed instead. The path to the playbook is relative to the molecule.yml location.
Normal side effect settings (from `provisioner.playbooks`) are ignored for action with
argument.

`verify` without an argument is executing usual tests configured in the verifier section
of molecule.yml.

If one or more arguments (separated by spaces) are present, each argument is treated
as a test name (file or directory) to pass to the verifier (either Ansible or Testinfra).
The kind of verifier is set in the `verifier` section of molecule.yml and is applied to all
`verify` actions in the scenario.

The path to tests is relative to the molecule.yml file location. The `additional_files_or_dirs`
setting for verifier is ignored if the `verify` action has an argument.

Multiple `side_effect` and `verify` actions can be used to a create a combination
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

## Verifier

Molecule handles role testing by invoking configurable verifiers.

### Ansible

::: molecule.verifier.ansible.Ansible

### Testinfra

::: molecule.verifier.testinfra.Testinfra
