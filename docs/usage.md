# Command Line Reference

## Special commands

- drivers
- init
- list
- login
- matrix
- reset

## Valid actions

- check
- cleanup

  - This action has cleanup and is not enabled by default.
    See the provisioner's documentation for further details.

- **converge** : Converge will execute the sequence necessary to converge the instances.
- create \*\* driver
- dependency
- destroy \*\* all, parallel, driver
- idempotence
- prepare \*\* force
- side-effect
- syntax
- test - \*\* - Test command will execute the sequence necessary to test the instances.
- verify

### -s, --scenario-name

### --parallel / --no-parallel

### Passing extra arguments to the provisioner

```
... -- -vvv --tags foo,bar

    Providing additional command line arguments to the `ansible-playbook`
    command.  Use this option with care, as there is no sanitation or
    validation of input.  Options passed on the CLI override options
    provided in provisioner's `options` section of `molecule.yml`.
```

## molecule init

### molecule init role

Initialize a new role using ansible-galaxy and include default
molecule directory. Please refer to the `init scenario`
command in order to generate a custom `molecule` scenario.

### molecule init scenario

## molecule list

List command shows information about current scenarios.

```
molecule list
```

## molecule login

## molecule matrix

Matrix will display the subcommand's ordered list of actions, which can
be changed in
[scenario](configuration.md#scenario)
configuration.
