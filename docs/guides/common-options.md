# Modular Common Options System

Molecule now provides a flexible modular system for applying common CLI options to commands, inspired by modern Click decorator patterns and the go.py example. This system allows command developers to compose exactly the options they need while keeping function signatures clean by accessing options through the context object.

## Overview

The traditional `@click_command_options` decorator applied all common options to every command as function parameters. The new modular system provides:

1. **Individual option decorators** for specific option groups
2. **A composer function** for combining multiple option groups
3. **Clean function signatures** - options accessed via `ctx.params`
4. **Full backward compatibility** with existing commands

## Key Pattern: Context-Based Access

Following the go.py pattern, common options are accessed through `ctx.params` rather than function parameters:

```python
@common_options('scenario', 'reporting')
@click.pass_context
def my_command(ctx):
    # Access options through context
    scenario_name = ctx.params['scenario_name']
    report = ctx.params['report']
    # ... command implementation
```

This keeps function signatures clean and follows Click best practices.

## Available Option Groups

### `scenario_options`

Adds scenario targeting options:

- `--scenario-name` / `-s`: Name of scenario to target
- `--all` / `--no-all`: Target all scenarios
- `--exclude` / `-e`: Exclude specific scenarios

### `reporting_options`

Adds reporting options:

- `--report` / `--no-report`: Enable end-of-run summary report

### `shared_state_options`

Adds experimental shared state options:

- `--shared-state` / `--no-shared-state`: Share state between scenarios
- `--shared-inventory` / `--no-shared-inventory`: Share inventory between scenarios

### `driver_options`

Adds driver selection options:

- `--driver-name` / `-d`: Name of driver to use

### `platform_options`

Adds platform targeting options:

- `--platform-name` / `-p`: Name of platform to target

### `parallel_options`

Adds parallel execution options:

- `--parallel` / `--no-parallel`: Enable parallel mode

### `destroy_options`

Adds destroy strategy options:

- `--destroy`: Destroy strategy (`always` or `never`)

## Usage Examples

### Individual Option Decorators

```python
from molecule.command.base import scenario_options, reporting_options

@click_command_ex()
@click.pass_context
@scenario_options
@reporting_options
def my_command(ctx: click.Context) -> None:
    """A command with only scenario and reporting options."""
    # Access options through context
    scenario_name = ctx.params['scenario_name']
    exclude = ctx.params['exclude']
    all_scenarios = ctx.params['__all']
    report = ctx.params['report']

    # Command implementation
```

### Common Options Composer

```python
from molecule.command.base import common_options

@click_command_ex()
@click.pass_context
@common_options('scenario', 'driver', 'reporting')
def my_command(ctx: click.Context) -> None:
    """A command using the composer for multiple option groups."""
    # Access options through context
    scenario_name = ctx.params['scenario_name']
    driver_name = ctx.params['driver_name']
    report = ctx.params['report']

    # Command implementation
```

### Using the Helper Function

```python
from molecule.command.base import common_options, get_common_args

@click_command_ex()
@click.pass_context
@common_options('scenario', 'driver', 'reporting')
def my_command(ctx: click.Context) -> None:
    """A command using the get_common_args helper."""
    # Get all common args at once
    args = get_common_args(ctx)

    scenario_name = args['scenario_name']
    driver_name = args['driver_name']
    report = args['report']

    # Command implementation
```

### Mixing with Custom Options

```python
from molecule.command.base import scenario_options

@click_command_ex()
@click.pass_context
@scenario_options
@click.option(
    "--force/--no-force",
    default=False,
    help="Force execution even if dangerous.",
)
def my_command(ctx: click.Context, force: bool) -> None:
    """A command mixing common options with custom ones."""
    # Common options through context
    scenario_name = ctx.params['scenario_name']
    all_scenarios = ctx.params['__all']

    # Custom option as parameter
    if force:
        # ... force logic
        pass
```

### Full-Featured Command

```python
from molecule.command.base import common_options, get_common_args

@click_command_ex()
@click.pass_context
@common_options('scenario', 'driver', 'platform', 'parallel', 'destroy', 'reporting', 'shared_state')
@click.argument("ansible_args", nargs=-1, type=click.UNPROCESSED)
def comprehensive_command(
    ctx: click.Context,
    ansible_args: tuple[str, ...],
) -> None:
    """A command demonstrating all available option groups."""
    # Get all common options at once
    args = get_common_args(ctx)

    # Access specific options
    scenario_name = args['scenario_name']
    driver_name = args['driver_name']
    parallel = args['parallel']

    # Command implementation
```

## Helper Functions

### `get_common_args(ctx)`

Extracts all common arguments from the context:

```python
args = get_common_args(ctx)
# Returns dict with only common parameters:
# {'scenario_name': [...], 'report': False, ...}
```

## Migration Guide

### Existing Commands

All existing commands continue to work unchanged. The original `@click_command_options` decorator remains available and functional.

### New Commands

New commands should follow the context-based pattern:

1. **Add `@click.pass_context`** to your command decorator stack
2. **Use `ctx` as first parameter** in your function signature
3. **Access options via `ctx.params['option_name']`**
4. **Use `get_common_args(ctx)` for convenience**

#### Before (old pattern):

```python
@click_command_options
def my_command(scenario_name, exclude, __all, report, ...):
    # Implementation
```

#### After (new pattern):

```python
@common_options('scenario', 'reporting')
@click.pass_context
def my_command(ctx):
    scenario_name = ctx.params['scenario_name']
    report = ctx.params['report']
    # Implementation
```

### Recommended Patterns

For commands that need:

- **Basic scenario handling**: `@scenario_options`
- **Scenario + reporting**: `@common_options('scenario', 'reporting')`
- **Full test command**: `@common_options('scenario', 'driver', 'platform', 'parallel', 'destroy', 'reporting', 'shared_state')`
- **Simple lifecycle command**: `@common_options('scenario', 'shared_state')`

## Benefits

1. **Cleaner function signatures**: No cluttered parameter lists
2. **Better option organization**: Logical grouping of related options
3. **Easier composition**: Pick only the options you need
4. **Better help text**: Users see only relevant options for each command
5. **Easier testing**: Test only the options that matter for each command
6. **Future extensibility**: Easy to add new option groups without affecting existing commands
7. **Follows Click conventions**: Uses context-based parameter access

## Error Handling

The system validates option group names at decoration time:

```python
@common_options('invalid_group')  # Raises ValueError
def my_command(ctx):
    pass
```

Available groups: `scenario`, `reporting`, `shared_state`, `driver`, `platform`, `parallel`, `destroy`

## Context Parameter Access

All common options are available through `ctx.params`:

| Option Group   | Parameters                          |
| -------------- | ----------------------------------- |
| `scenario`     | `scenario_name`, `exclude`, `__all` |
| `reporting`    | `report`                            |
| `shared_state` | `shared_state`, `shared_inventory`  |
| `driver`       | `driver_name`                       |
| `platform`     | `platform_name`                     |
| `parallel`     | `parallel`                          |
| `destroy`      | `destroy`                           |
