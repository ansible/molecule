## Concurrent scenario execution with `--workers`

!!! warning

    This functionality should be considered experimental.

When testing Ansible collections with many scenarios, Molecule can run
scenarios concurrently using the `--workers` flag. This uses a process
pool to execute multiple scenarios in parallel while the default
scenario's `create` and `destroy` lifecycle runs serially in the main
process.

### Usage

```bash
# Run with 4 concurrent workers
molecule test --all --workers 4

# Use all available CPU cores
molecule test --all --workers cpus

# Use all cores minus one (leaves headroom for the system)
molecule test --all --workers cpus-1
```

### Requirements

- **Collection mode** -- `--workers` > 1 requires a valid `galaxy.yml` in the
  current directory (i.e., you must be in a collection).
- **Shared state** -- scenarios should use `shared_state: true` in their
  `molecule.yml` so that the default scenario handles infrastructure
  create/destroy while workers run the test sequences.

### Scenario slicing with `--slice`

When scenario names contain directory separators (e.g.
`appliance_vlans/gathered`, `appliance_vlans/merged`), the `--slice`
flag controls how scenarios are grouped into work units dispatched to
workers.

| `--slice` | Behavior |
|-----------|----------|
| `1` (default) | Group by the first path segment — all CRUD states for a resource run sequentially on one worker. |
| `2` | Each leaf scenario is an independent work unit (no grouping). |

```bash
# Group by resource (default when --workers is used)
molecule test --all --workers 4

# Treat each scenario independently
molecule test --all --workers 4 --slice 2
```

`slice` can also be set in the config file (`config.yml` or
`molecule.yml`) so it travels with the project:

```yaml
# extensions/molecule/config.yml
shared_state: true
slice: 1
```

The CLI flag overrides the config value when both are present.

For example, with 186 scenarios across 37 resources, `slice: 1`
produces 37 work units instead of 186, each containing ~5 scenarios
that run sequentially within the worker.

The CLI `--slice` flag requires `--workers` > 1. When defined only
in the config file, `slice` is silently ignored in sequential mode.

### How it works

1. The **default scenario's `create`** runs first (serial, main process).
2. Prerun tasks run for all scenarios (serial, main process).
3. Scenarios are grouped into slices according to `--slice` depth and
   submitted to a `ProcessPoolExecutor` with the specified number of
   workers. Each worker reconstructs a `Config` from each scenario's
   `molecule.yml` and runs the scenario's sequence, skipping `create`
   and `destroy` (handled by the default scenario).
4. Results are collected as workers complete.
5. The **default scenario's `destroy`** runs last (serial, main process).

### Failure handling

By default, Molecule uses **fail-fast** behavior: when a scenario fails,
no new scenarios are started (workers already running finish their
current scenario), then destroy runs.

Use `--continue-on-failure` to run all remaining scenarios even after a
failure:

```bash
molecule test --all --workers 4 --continue-on-failure
```

### Incompatible options

- `--workers` > 1 cannot be combined with `--destroy=never`.
- `--slice` cannot be used when `--workers` is 1 (no parallelism).

---

## Legacy: `--parallel` isolation mode (deprecated)

!!! warning

    The `--parallel` flag is deprecated and will be removed in a future
    release. Use `--workers` instead for native concurrent execution.

The `--parallel` flag provides process **isolation** (UUID-based
ephemeral directories, platform name suffixing, file locking) so that
external tools like [GNU Parallel](https://www.gnu.org/software/parallel/)
or [Pytest](https://docs.pytest.org/en/latest/) can orchestrate multiple
Molecule processes without conflicts. Molecule itself does not spawn
concurrent work in this mode.

```bash
# Deprecated -- use --workers instead
molecule test --parallel
```

Supported sequences: `check`, `destroy`, `test`.
