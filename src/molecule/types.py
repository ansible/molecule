"""Assorted convenience types for molecule."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict


if TYPE_CHECKING:
    from collections.abc import MutableMapping
    from typing import Any, Literal, TypeAlias

    Options: TypeAlias = MutableMapping[str, str | bool]


class DependencyData(TypedDict, total=False):
    """Molecule dependency configuration.

    Attributes:
        name: Dependency name.
        command: Command to run for dependency.
        enabled: Is this dependency enabled.
        options: Options for this dependency.
        env: Environment variables related to this dependency.
    """

    name: str
    command: str | None
    enabled: bool
    options: Options
    env: dict[str, str]


class DriverOptions(TypedDict, total=False):
    """Config options for molecule drivers.

    Attributes:
        ansible_connection_options: Options to use with ansible connection plugin.
        login_cmd_template: Template with which to generate login commands.
        managed: Whether the driver is managed.
    """

    ansible_connection_options: dict[str, str]
    login_cmd_template: str
    managed: bool


class DriverData(TypedDict, total=False):
    """Molecule driver configuration.

    Attributes:
        name: Driver name.
        provider:
        options: Options for this driver.
        ssh_connection_options: SSH-specific options.
        safe_files: A list of safe files.
    """

    name: str
    provider: dict[str, Any]
    options: DriverOptions
    ssh_connection_options: list[str]
    safe_files: list[str]


class InventoryData(TypedDict):
    """Inventory data for a molecule run.

    Attributes:
        hosts: A list of hosts.
        host_vars: A dictionary of ansible host_vars.
        group_vars: A dictionary of ansible group_vars.
        links: ???
    """

    hosts: dict[str, str]
    host_vars: dict[str, str]
    group_vars: dict[str, str]
    links: dict[str, str]


class PlatformData(TypedDict, total=False):
    """Platform data for a Molecule run.

    Attributes:
        name: Name of the platform.
        groups: Optional list of groups.
        children: Optional list of child groups.
    """

    name: str
    groups: list[str]
    children: list[str]


class PlaybookData(TypedDict, total=False):
    """Playbooks for a scenario.

    Attributes:
        cleanup: The cleanup playbook.
        create: The create playbook.
        converge: The converge playbook.
        destroy: The destroy playbook.
        prepare: The prepare playbook.
        side_effect: The side_effect playbook.
        verify: The verify playbook.
    """

    cleanup: str
    create: str
    converge: str
    destroy: str
    prepare: str
    side_effect: str
    verify: str


class ProvisionerData(TypedDict, total=False):
    """Molecule provisioner configuration.

    Attributes:
        name: Name of the provisioner.
        config_options: Configuration options.
        ansible_args: Arguments to use with ansible.
        connection_options: Options for the connection.
        options: Options for this provisioner.
        env: Environment variables for this provisioner.
        inventory: Inventory config.
        children: Children of this provisioner.
        playbooks: Playbooks for use in the provisioner.
        log: Should this be logged.
    """

    name: str
    config_options: dict[str, Any]
    ansible_args: list[str]
    connection_options: dict[str, Any]
    options: Options
    env: dict[str, str]
    inventory: InventoryData
    children: dict[str, Any]
    playbooks: PlaybookData
    log: bool


class ScenarioData(TypedDict):
    """Molecule scenario configuration.

    Attributes:
        name: Name of the scenario.
        check_sequence: Sequence of tasks to run for 'check'.
        cleanup_sequence: Sequence of tasks to run for 'cleanup'.
        converge_sequence: Sequence of tasks to run for 'converge'.
        create_sequence: Sequence of tasks to run for 'create'.
        destroy_sequence: Sequence of tasks to run for 'destroy'.
        test_sequence: Sequence of tasks to run for 'test'.
    """

    name: str
    check_sequence: list[str]
    cleanup_sequence: list[str]
    converge_sequence: list[str]
    create_sequence: list[str]
    destroy_sequence: list[str]
    test_sequence: list[str]


class VerifierData(TypedDict, total=False):
    """Molecule verifier configuration.

    Attributes:
        name: Name of the verifier.
        directory: Verifier directory name.
        enabled: Is the verifier enabled.
        options: Options to apply to the verifier.
        env: Applicable environment variables.
        additional_files_or_dirs: Additional paths to verify.
    """

    name: str
    directory: str
    enabled: bool
    options: Options
    env: dict[str, str]
    additional_files_or_dirs: list[str]


class ConfigData(TypedDict):
    """Class representing molecule config.

    Attributes:
        dependency: Dependency config.
        driver: Driver config.
        platforms: List of platforms.
        prerun: Should prerun tasks be run.
        role_name_check: ???
        provisioner: Provisioner config.
        scenario: Scenario config.
        verifier: Verifier config.
    """

    dependency: DependencyData
    driver: DriverData
    platforms: list[PlatformData]
    prerun: bool
    role_name_check: int
    provisioner: ProvisionerData
    scenario: ScenarioData
    verifier: VerifierData


class MoleculeArgs(TypedDict, total=False):
    """Class representing base arguments passed to all Molecule commands.

    Attributes:
        base_config: paths of base config files to load in order.
        debug: Whether to enable debug logging.
        env_file: File to read environment variables from.
        verbose: Verbosity level.
    """

    base_config: list[str]
    debug: bool
    env_file: str
    verbose: int


class CommandArgs(TypedDict, total=False):
    """Class representing commandline arguments passed to molecule.

    These arguments may or may not be passed depending on the command being called.

    Attributes:
        destroy: Destroy strategy to use.
        driver_name: Name of driver to use.
        force: Whether to enable force mode.
        format: Output format
        host: Host to access.
        parallel: Whether to enable parallel mode.
        platform_name: Name of the platform to target.
        scenario_name: Name of the scenario to target.
        subcommand: Name of subcommand being run.
    """

    destroy: Literal["always", "never"]
    driver_name: str
    force: bool
    format: Literal["simple", "plain", "yaml"]
    host: str
    parallel: bool
    platform_name: str
    scenario_name: str
    subcommand: str
