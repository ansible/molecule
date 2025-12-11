# Molecule Execution

This document aims to describe how molecule execution goes from commandline to playbook execution. It assumes you have a basic understanding of Molecule
scenarios and playbooks.

## Molecule CLI

The basic execution starts with `shell.py`. Molecule uses Click for CLI options, and the base arguments and individual subcommands are registered here.

## Subcommands

Each Molecule subcommand is represented by a file in `command/`. These files contain two important chunks of code: the command class, and a function that defines
the commandline arguments for the subcommand. Because Molecule uses Click, the function is decorated with click decorators to define arguments and options.
These are all centrally defined in `click_cfg.py`, so that options can be applied consistently across commands.

The function's job is to take the options passed in from Click and arrange them into a standard format for use by Molecule. These structures are `MoleculeArgs`,
`CommandArgs`, and `ansible_args`, for options relating to Molecule run, command execution, and Ansible invocation, respectively. `CommandArgs` and `MoleculeArgs` are
both nested TypedDicts defined in `types.py`, while `ansible_args` is a simple tuple of strings. Those three are passed to
`command/base.py:execute_cmdline_scenarios()` along with the scenario include and exclude lists to actually run the specified scenarios.

## Base Command Module

`command/base.py` has a lot going on, but most of it concerns taking the arguments passed in from the commandline and package them into `Scenario` objects for
execution.

### Config Object

The `Config` object holds the computed configuration for the running molecule scenario, generated from the root Molecule config, the scenario Molecule config,
commandline options, and environment variables. This object lives in the `Scenario` object to provide guidance for scenario execution.

### Scenario Object

The `Scenario` object contains the `Config` object for the scenario in question, as well as helper properties for things like subcommand sequences which may vary
between scenarios. Multiple `Scenario` objects are contained in a `Scenarios` object which guides the total runtime of the Molecule execution

### Scenarios Object

The `Scenarios` object contains a sequence of `Scenario` objects as well as some methods to produce a deterministic order of playbooks to run to execute them
all.

The base command module's `execute_cmdline_scenarios()` function thus generates config objects based on scenario names passed in, creates a `Scenarios` object
with those configs (which internally creates the `Scenario` objects for individual processing), and then runs those scenarios by passing each `Scenario` to the
`execute()` method of the relevant subcommand command class.

## Back to Subcommands

Each subcommand's command class (inheriting from `command.base.Base`) has an `execute()` method that takes the `Scenario` object and its `Config` and passes the
relevant details for this command to the provisioner, which finally runs the playbook. At this point, all details have been fleshed out: the scenarios to run,
the sequence of actions to take on each scenario, all the configuration, and so each command's `execute()` method is called on each scenario in turn.

## Provisioner

The provisioner has a number of methods covering each subcommand, which call the underlying `AnsiblePlaybook.execute()` method for the appropriate playbook for
the scenario. Like `Scenario`s, these are also wrapped in an `AnsiblePlaybooks` object, but here instead of a sequence of contained objects, it acts more like a
map, ensuring that the correct playbook can easily be called for each action.

It is at this step when the call to `ansible-playbook` or `ansible-navigator` is finally run, and results from that are saved to the `Scenario` that requested
it, and then back to the `Scenarios` object that held the `Scenario`, and then finally those results can be presented back to the user at the end of
`execute_cmdline_scenarios()` if the user has requested it, at which point the execution is finally complete.
