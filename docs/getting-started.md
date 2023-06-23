# Getting Started Guide

The following guide will step through an example of developing and
testing a new Ansible role. After reading this guide, you should be
familiar with the basics of how to use Molecule and what it can offer.

!!! note

    In order to complete this guide by hand, you will need to additionally
    install [Docker](https://docs.docker.com/). Molecule requires an
    external Python dependency for the Docker driver which is provided when
    installing Molecule using `pip install 'molecule-plugins[docker]'`.

## Creating a new role

Molecule uses [ansible-galaxy](https://docs.ansible.com/ansible/latest/cli/ansible-galaxy.html) under the hood to generate conventional role layouts. If
you've ever worked with Ansible roles before, you'll be right at home.
If not, please review the
[role directory structure](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_roles.html#role-directory-structure)
guide to see what each folder is responsible for.

To generate a new role with Molecule, simply run:

```shell
$ molecule init role acme.my_new_role --driver-name docker
```

You should then see a `my_new_role` folder in your current directory.

!!! note

    For future reference, if you want to initialize Molecule within an
    existing role, you would use the
    `molecule init scenario -r my_role_name` command from within the role's
    directory (e.g. `my_role_name/`).

## Molecule Scenarios

You will notice one new folder which is the `molecule` folder.

In this folder there is a single `root_scenario` called `default`.

Scenarios are the starting point for a lot of powerful functionality
that Molecule offers. For now, we can think of a scenario as a test
suite for your newly created role. You can have as many scenarios as you
like and Molecule will run one after the other.

## The Scenario Layout

Within the `molecule/default` folder, we find a number of files and
directories:

```bash
$ ls
INSTALL.rst  molecule.yml  converge.yml  verify.yml
```

- `INSTALL.rst` contains instructions on what additional software or
  setup steps you will need to take in order to allow Molecule to
  successfully interface with the driver.
- `molecule.yml` is the central configuration entrypoint for Molecule.
  With this file, you can configure each tool that Molecule will
  employ when testing your role.
- `converge.yml` is the playbook file that contains the call for your
  role. Molecule will invoke this playbook with `ansible-playbook` and
  run it against an instance created by the driver.
- `verify.yml` is the Ansible file used for testing as Ansible is the
  default [verifier](configuration.md#verifier). This allows you to
  write specific tests against the state of the container after your
  role has finished executing. Other verifier tools are available
  Note that [testinfra](https://testinfra.readthedocs.io/en/latest/) was the default verifier prior to molecule version 3.

!!! note

    If the `verify.yml` playbook does not explicitly `include_role` your
    role, the `library` and `module_utils` provided by your role are not
    available in the playbook by default. If you need those for testing but
    would like to avoid re-running your role, consider adding an empty task
    file `init.yml` to your role and use `tasks_from` to include your role
    in the `verify.yml` playbook:

    ``` yaml
    - name: Verify
        hosts: all
        become: true
        tasks:
        - name: Initialize role without actually running it
            ansible.builtin.include_role:
            name: my_role
            tasks_from: init

    # Start testing: can use role library now
    ```

## Inspecting the `molecule.yml`

The `molecule.yml` is for configuring Molecule. It is a
[YAML](https://yaml.org/) file whose keys represent the high level
components that Molecule provides. These are:

- The [dependency](configuration.md#dependency) manager. Molecule
  uses [galaxy development guide]
  by default to resolve your role dependencies.
- The [driver](configuration.md#driver) provider. Molecule uses
  [Docker](https://docs.docker.com/) by default. Molecule uses the
  driver to delegate the task of creating instances.
- The [platforms](configuration.md#platforms) definitions. Molecule
  relies on this to know which instances to create, name and to which
  group each instance belongs. If you need to test your role against
  multiple popular distributions (CentOS, Fedora, Debian), you can
  specify that in this section.
- The [provisioner](configuration.md#provisioner). Molecule only
  provides an Ansible provisioner. Ansible manages the life cycle of
  the instance based on this configuration.
- The [scenario][] definition.
  Molecule relies on this configuration to control the scenario
  sequence order.
- The [verifier](configuration.md#verifier) framework. Molecule
  uses Ansible by default to provide a way to write specific state
  checking tests (such as deployment smoke tests) on the target
  instance.

## Run test sequence commands

Let's create the first Molecule managed instance with the Docker
driver.

First, ensure that [Docker](https://docs.docker.com/) is running with
the typical sanity check:

```bash
$ docker run hello-world
```

Now, we can tell Molecule to create an instance with:

```bash
$ molecule create
```

We can verify that Molecule has created the instance and they're up and
running with:

```bash
$ molecule list
```

Now, let's add a task to our `tasks/main.yml` like so:

```yaml
- name: Molecule Hello World!
  ansible.builtin.debug:
    msg: Hello, World!
```

We can then tell Molecule to test our role against our instance with:

```bash
$ molecule converge
```

If we want to manually inspect the instance afterwards, we can run:

```bash
$ molecule login
```

We now have a free hand to experiment with the instance state.

Finally, we can exit the instance and destroy it with:

```bash
$ molecule destroy
```

!!! note

    If Molecule reports any errors, it can be useful to pass the `--debug`
    option to get more verbose output.

## Run a full test sequence

Molecule provides commands for manually managing the lifecycle of the
instance, scenario, development and testing tools. However, we can also
tell Molecule to manage this automatically within a
`root_scenario` sequence.

The full lifecycle sequence can be invoked with:

```bash
$ molecule test
```

!!! note

    It can be particularly useful to pass the `--destroy=never` flag when
    invoking `molecule test` so that you can tell Molecule to run the full
    sequence but not destroy the instance if one step fails.

    If the `--platform-name=[PLATFORM_NAME]` flag is passed or the
    environment variable `MOLECULE_PLATFORM_NAME` is exposed when invoking
    `molecule test`, it can tell Molecule to run the test in one platform
    only. It is useful if you want to test one platform docker image.

[galaxy development guide]: https://docs.ansible.com/ansible/latest/galaxy/dev_guide.html
