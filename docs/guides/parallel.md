## Running Molecule processes in parallel mode

!!! warning

    This functionality should be considered experimental. It is part of
    ongoing work towards enabling parallelizable functionality across all
    moving parts in the execution of the Molecule feature set.

!!! note

    Only the following sequences support parallelizable functionality:

    > -   `check_sequence`: `molecule check --parallel`
    > -   `destroy_sequence`: `molecule destroy --parallel`
    > -   `test_sequence`: `molecule test --parallel`

    It is currently only available for use with the Docker driver.

When Molecule receives the `--parallel` flag it will generate a
[UUID](https://en.wikipedia.org/wiki/Universally_unique_identifier) for
the duration of the testing sequence and will use that unique identifier
to cache the run-time state for that process. The parallel Molecule
processes cached state and created instances will therefore not
interfere with each other.

Molecule uses a new and separate caching folder for this in the
`$HOME/.cache/molecule_parallel` location. Molecule exposes a new
environment variable `MOLECULE_PARALLEL` which can enable this
functionality.

It is possible to run Molecule processes in parallel using another tool
to orchestrate the parallelization (such as [GNU
Parallel](https://www.gnu.org/software/parallel/) or
[Pytest](https://docs.pytest.org/en/latest/)). If you do so, make sure
Molecule knows it is running in parallel mode by specifying the
`--parallel` flag to your command(s) to avoid concurrency issues.
