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

### molecule init scenario

## molecule list

List command shows information about current scenarios.

```
molecule list
```

## molecule login

<<<<<<< HEAD
When using a pre ansible-native configuration, if configured, Molecule has per resource awareness and can
facilitate an interactive connection to a system.

When using an ansible-native configuration, the same connection methods used to connect to production systems
are available.

Options leveraging the resources defined in the ansible inventory include:

- [ansible adhoc commands](https://docs.ansible.com/ansible/latest/command_guide/intro_adhoc.html)

- [ansible-console](https://docs.ansible.com/ansible/latest/cli/ansible-console.html)
=======
When using a pre ansible-native configuration, if configured,  Molecule has per resource awareness and can
facilitate an interactive connection to a system.

When using an ansible-native configuration, the same connection methods used to connect to production systems
are available. 

Options leveraging the resources defined in the ansible inventory include:

  - [ansible adhoc commands](https://docs.ansible.com/ansible/latest/command_guide/intro_adhoc.html)

  - [ansible-console](https://docs.ansible.com/ansible/latest/cli/ansible-console.html)
>>>>>>> 6d7764cd (Add documentation links to molecule login error messages)

Resource native connection options include:

- `SSH`

- `podman exec`

- `curl`

- `psql`, `mysql`, and `mongosh`

- `oc`, `kubectl`, and `odo`

- etc

## molecule matrix

Matrix will display the subcommand's ordered list of actions, which can
be changed in
[scenario](configuration.md#scenario)
configuration.

## Test sequence commands

We can tell Molecule to create an instance with:

```bash
molecule create
```

We can verify that Molecule has created the instance and they're up and
running with:

```bash
molecule list
```

Now, let's add a task to our role under `tasks/main.yml` file like so:

```yaml
- name: Molecule Hello World!
  ansible.builtin.debug:
    msg: Hello, World!
```

We can then tell Molecule to test our role against our instance with:

```bash
molecule converge
```

If we want to manually inspect the instance afterward, we can run:

```bash
molecule login
```

We now have a free hand to experiment with the instance state.

Finally, we can exit the instance and destroy it with:

```bash
molecule destroy
```

!!! note

    If Molecule reports any errors, it can be useful to pass the `--debug`
    option to get more verbose output.
