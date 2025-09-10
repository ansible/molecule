#  Copyright (c) 2015-2018 Cisco Systems, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
"""Molecule Utils Module."""

from __future__ import annotations

import copy
import fnmatch
import logging
import os
import re
import sys

from pathlib import Path
from typing import TYPE_CHECKING, overload

import click
import jinja2
import yaml

from ansible_compat.ports import cache

from molecule.constants import (
    MOLECULE_COLLECTION_GLOB,
    MOLECULE_COLLECTION_ROOT,
    MOLECULE_GLOB,
    MOLECULE_HEADER,
    MOLECULE_ROOT,
)
from molecule.exceptions import MoleculeError


if TYPE_CHECKING:
    from collections.abc import Generator, Iterable, MutableMapping, Sequence
    from io import TextIOWrapper
    from typing import Any, NoReturn, TypeVar
    from warnings import WarningMessage

    from molecule.types import CollectionData, CommandArgs, ConfigData, Options, PlatformData

    NestedDict = MutableMapping[str, Any]
    _T = TypeVar("_T", bound=NestedDict)


LOG = logging.getLogger(__name__)


class SafeDumper(yaml.SafeDumper):
    """SafeDumper YAML Class."""

    def increase_indent(
        self,
        flow: bool = False,  # noqa: FBT001, FBT002
        indentless: bool = False,  # noqa: ARG002, FBT001, FBT002
    ) -> None:
        """Increase indent of the YAML structure.

        Args:
            flow: Whether to reset indenting on newline.
            indentless: Whether to skip additional indenting.
        """
        return super().increase_indent(flow, indentless=False)


def print_environment_vars(env: dict[str, str] | None) -> None:
    """Log ``Ansible`` and ``Molecule`` environment variables and returns None.

    Args:
        env: A dict containing the shell's environment as collected by ``os.environ``.
    """
    if not env:
        return

    logger = logging.getLogger(__name__)

    sections: dict[str, list[tuple[str, str]]] = {}

    for n in ["ANSIBLE", "MOLECULE"]:
        sections[n] = [(k, v) for (k, v) in sorted(env.items()) if k.startswith(f"{n}_")]
        logger.debug("%s ENVIRONMENT:\n%s\n", n, "\n".join(f"{k}: {v}" for (k, v) in sections[n]))

    logger.debug(
        "SHELL REPLAY: %s",
        " ".join(f"{k}={v}" for _, es in sections.items() for (k, v) in es),
    )


def sysexit(code: int = 1) -> NoReturn:
    """Perform a system exit with given code.

    Args:
        code: The return code to emit.
    """
    sys.exit(code)


def sysexit_with_message(
    msg: str,
    code: int = 1,
    warns: Sequence[WarningMessage] = (),
) -> NoReturn:
    """Wrapper around sysexit to also display a message.

    Args:
        msg: The message to display.
        code: The return code to exit with.
        warns: A series of warnings to send alongside the message.
    """
    for warning in warns:
        LOG.warning(warning.message)

    # For success (code 0), always use info logging
    # For failures (code != 0), use debug-aware logging
    if code == 0:
        LOG.info(msg)
    else:
        # Show only the error message in normal mode for failures
        LOG.error(msg)

    sysexit(code)


def sysexit_from_exception(exc: MoleculeError) -> NoReturn:
    """Wrapper for sysexit to display messages and use return code from an exception.

    Args:
        exc: The exception to determine exit values from.
    """
    # Check if debug mode is enabled
    ctx = click.get_current_context(silent=True)
    debug_mode = False
    if ctx and ctx.obj and isinstance(ctx.obj, dict):
        debug_mode = ctx.obj.get("args", {}).get("debug", False)

    if debug_mode:
        # Show full traceback in debug mode for failures
        LOG.exception(exc.message)
        sysexit(exc.code)
    else:
        sysexit_with_message(exc.message, exc.code)


def os_walk(
    directory: str | Path,
    pattern: str,
    excludes: list[str] | None = None,
    *,
    followlinks: bool = False,
) -> Generator[str, None, None]:
    """Navigate recursively and retried files based on pattern.

    Args:
        directory: The base directory.
        pattern: A pattern against which to match files on.
        excludes: A list of directory names to not look in.
        followlinks: Whether or not to follow symbolic links.

    Yields:
        File paths that match the filters provided.
    """
    if excludes is None:
        excludes = []

    for root, dirs, files in os.walk(directory, topdown=True, followlinks=followlinks):
        dirs[:] = [d for d in dirs if d not in excludes]
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = Path(root) / basename

                yield str(filename)


def render_template(template: str, **kwargs: str | dict[str, str]) -> str:
    """Render a jinaj2 template.

    Args:
        template: The jinja template to render.
        **kwargs: Values to render in the template.

    Returns:
        The rendered template.
    """
    t = jinja2.Environment(
        autoescape=jinja2.select_autoescape(
            default_for_string=False,
            default=False,
        ),
    )
    return t.from_string(template).render(kwargs)


def write_file(filename: str | Path, content: str, header: str | None = None) -> None:
    """Write a file with the given filename and content.

    Args:
        filename: The target file.
        content: A string containing the data to be written.
        header: A header, if None it will use default header.
    """
    if header is None:
        content = MOLECULE_HEADER + "\n\n" + content

    if isinstance(filename, str):
        filename = Path(filename)
    filename.parent.mkdir(exist_ok=True)
    filename.write_text(content)


def molecule_prepender(content: str) -> str:
    """Return molecule identification header.

    Args:
        content: Molecule content to prepend.

    Returns:
        Provided content prepended with MOLECULE_HEADER.
    """
    return MOLECULE_HEADER + "\n\n" + content


def file_prepender(filename: str | Path) -> None:
    """Prepend an informational header on files managed by Molecule and returns None.

    Args:
        filename: A string containing the target filename.
    """
    if isinstance(filename, str):
        filename = Path(filename)

    with filename.open("r+") as f:
        content = f.read()
        f.seek(0, 0)
        f.write(molecule_prepender(content))


def safe_dump(data: object, explicit_start: bool = True) -> str:  # noqa: FBT001, FBT002
    """Dump the provided data to a YAML document and returns a string.

    Args:
        data: The object to dump.
        explicit_start: An optional bool to toggle explicit document start.

    Returns:
        The YAML document in a string.
    """
    return yaml.dump(
        data,
        Dumper=SafeDumper,
        default_flow_style=False,
        explicit_start=explicit_start,
    )


def safe_load(string: str | TextIOWrapper):  # type: ignore[no-untyped-def]  # noqa: ANN201
    """Parse the provided string returns a dict.

    Args:
        string: A string to be parsed.

    Returns:
        A dict of the parsed string.


    Raises:
        MoleculeError: when YAML loading fails.
    """
    try:
        return yaml.safe_load(string) or {}
    except yaml.scanner.ScannerError as e:
        raise MoleculeError(str(e)) from None
    return {}


def safe_load_file(filename: str | Path):  # type: ignore[no-untyped-def]  # noqa: ANN201
    """Parse the provided YAML file and returns a dict.

    Args:
        filename: The file to parse.

    Returns:
        A dict of the parsed string.
    """
    if isinstance(filename, str):
        filename = Path(filename)

    with filename.open() as stream:
        return safe_load(stream)


def instance_with_scenario_name(instance_name: str, scenario_name: str) -> str:
    """Format instance name that includes scenario.

    Args:
        instance_name: Name of the instance.
        scenario_name: Name of the scenario.

    Returns:
        Combined instance and scenario names.
    """
    return f"{instance_name}-{scenario_name}"


def verbose_flag(options: Options) -> list[str]:
    """Return computed verbosity flag.

    Args:
        options: Full commandline options list.

    Returns:
        The appropriate verbosity option.
    """
    verbose = "v"
    flags = []
    for _i in range(3):
        if options.get(verbose):
            flags = [f"-{verbose}"]
            del options[verbose]
            if options.get("verbose"):
                del options["verbose"]
            break
        verbose = verbose + "v"

    return flags


def filter_verbose_permutation(options: Options) -> Options:
    """Clean verbose information.

    Args:
        options: Dictionary of commandline options.

    Returns:
        Dictionary of options without verbose options included.
    """
    return {k: options[k] for k in options if not re.match(r"^[v]+$", k)}


@overload
def abs_path(path: Path) -> Path: ...


@overload
def abs_path(path: str | None) -> str: ...


def abs_path(path: str | Path | None) -> str | Path:
    """Return absolute path.

    Args:
        path: File path to create absolute path from.

    Returns:
        Absolute path of path.
    """
    if not path:
        return ""

    output_type = type(path)
    if isinstance(path, Path):
        path = str(path)
    path = os.path.abspath(path)  # noqa: PTH100

    return output_type(path)


def merge_dicts(a: _T, b: _T) -> _T:
    """Merge the values of b into a and returns a new dict.

    This function uses the same algorithm as Ansible's `combine(recursive=True)` filter.

    Args:
        a: the target dictionary
        b: the dictionary to import

    Returns:
        A dictionary with b applied on to a
    """
    result = copy.deepcopy(a)

    for k, b_v in b.items():
        a_v = a.get(k)
        if a_v is not None and isinstance(a_v, dict) and isinstance(b_v, dict):
            result[k] = merge_dicts(a_v, b_v)
        else:
            result[k] = b_v

    return result


def validate_parallel_cmd_args(cmd_args: CommandArgs) -> None:
    """Prevents use of options incompatible with parallel mode.

    Args:
        cmd_args: Arguments to validate.

    Raises:
        MoleculeError: when incompatible options are present.
    """
    if cmd_args.get("parallel") and cmd_args.get("destroy") == "never":
        msg = 'Combining "--parallel" and "--destroy=never" is not supported'
        raise MoleculeError(msg)


def _parallelize_platforms(
    config: ConfigData,
    run_uuid: str,
) -> list[PlatformData]:
    def parallelize(platform: PlatformData) -> PlatformData:
        platform["name"] = f"{platform['name']}-{run_uuid}"
        return platform

    return [parallelize(platform) for platform in config["platforms"]]


def _filter_platforms(
    config: ConfigData,
    platform_name: str,
) -> list[PlatformData]:
    for platform in config["platforms"]:
        if platform["name"] == platform_name:
            return [platform]

    return []


@cache
def find_vcs_root(
    location: str | Path = "",
    dirs: tuple[str, ...] = (".git", ".hg", ".svn"),
    default: str = "",
) -> str:
    """Return current repository root directory.

    Args:
        location: Location to begin searching from.
        dirs: VCS config directory names to look for.
        default: Default value to return if no VCS directory found.

    Returns:
        The ancestor path containing VCS folders or default if none are found.
    """
    if not location:
        location = Path.cwd()
    if isinstance(location, str):
        location = Path(location)

    prev, location = None, location.absolute()
    while prev != location:
        if any((location / d).is_dir() for d in dirs):
            return str(location)
        prev, location = (location, location.parent)
    return default


def lookup_config_file(filename: str) -> str | None:
    """Return config file PATH.

    Args:
        filename: Config file name to find.

    Returns:
        Path to config file or None if not found.
    """
    # project root
    search_paths = [Path(find_vcs_root(default="~")) / filename]

    # collection path
    collection_dir, _ = get_collection_metadata()
    if collection_dir:
        search_paths.append(Path(collection_dir / MOLECULE_COLLECTION_ROOT / Path(filename).name))

    # home directory
    search_paths.append(Path.home() / filename)

    for path in search_paths:
        if path.is_file():
            LOG.info("Found config file %s", path)
            return str(path)
    return None


def boolean(value: object, *, default: bool | None = None) -> bool:
    """Evaluate any object as boolean matching ansible behavior.

    Args:
        value: The value to evaluate as a boolean.
        default: If provided, return this value for invalid inputs instead of raising TypeError.

    Returns:
        The boolean value of value, or default if value is invalid and default is provided.

    Raises:
        TypeError: If value does not resolve to a valid boolean and no default is provided.
    """
    # Based on https://github.com/ansible/ansible/blob/devel/lib/ansible/module_utils/parsing/convert_bool.py

    BOOLEANS_TRUE = frozenset(  # noqa: N806
        ("y", "yes", "on", "1", "true", "t", 1, 1.0, True),
    )
    BOOLEANS_FALSE = frozenset(  # noqa: N806
        ("n", "no", "off", "0", "false", "f", 0, 0.0, False, ""),
    )
    BOOLEANS = BOOLEANS_TRUE.union(BOOLEANS_FALSE)  # noqa: N806

    if isinstance(value, bool):
        return value

    normalized_value = str(value).lower().strip()

    if normalized_value in BOOLEANS_TRUE:
        return True
    if normalized_value in BOOLEANS_FALSE:
        return False

    # If we have a default, return it for invalid values
    if default is not None:
        return default

    raise TypeError(  # noqa: TRY003
        f"The value '{value!s}' is not a valid boolean.  Valid booleans include: {', '.join(repr(i) for i in BOOLEANS)!s}",  # noqa: EM102
    )


def dict2args(data: MutableMapping[str, str | bool]) -> list[str]:
    """Convert a dictionary of options to command like arguments.

    Args:
        data: Arguments dictionary to flatten.

    Returns:
        A list of command-like flags represented by the dictionary.
    """
    result = []
    # keep sorting in order to achieve a predictable behavior
    for k, v in sorted(data.items()):
        if v is not False:
            prefix = "-" if len(k) == 1 else "--"
            result.append(f"{prefix}{k}".replace("_", "-"))
            if v is not True:
                # { foo: True } should produce --foo without any values
                result.append(v)
    return result


def bool2args(data: bool | list[str]) -> list[str]:  # noqa: ARG001, FBT001
    """Convert a boolean value to command line argument (flag).

    Args:
        data: A boolean value.

    Returns:
        An empty list
    """
    return []


def oxford_comma(listed: Iterable[bool | str | Path], condition: str = "and") -> str:
    """Format a list into a sentence.

    Args:
        listed: List of string entries to modify
        condition: String to splice into string, usually 'and'

    Returns:
        Modified string
    """
    match [f"'{entry!s}'" for entry in listed]:
        case [one]:
            return one
        case [one, two]:
            return f"{one} {condition} {two}"
        case [*front, back]:
            return f"{', '.join(s for s in front)}, {condition} {back}"
        case _:
            return ""


@cache
def get_collection_metadata() -> tuple[Path, CollectionData] | tuple[None, None]:
    """Get collection directory and metadata.

    Returns:
        Tuple of (collection_directory, collection_data) if in a valid collection,
        or (None, None) if not in collection or galaxy.yml is invalid.
        Collection data dict contains at least 'name' and 'namespace' keys.
        Only returns collection info when galaxy.yml is valid.
    """
    cwd = Path.cwd()
    galaxy_file = cwd / "galaxy.yml"

    try:
        galaxy_data: CollectionData = safe_load_file(galaxy_file)
        important_keys = {"name", "namespace"}

        if not isinstance(galaxy_data, dict):
            LOG.warning("Invalid galaxy.yml format at %s", galaxy_file)
            return None, None

        if missing_keys := important_keys.difference(galaxy_data.keys()):
            LOG.warning(
                "galaxy.yml at %s is missing required fields: %s",
                galaxy_file,
                oxford_comma(missing_keys),
            )
            return None, None
    except FileNotFoundError:
        LOG.debug("No galaxy.yml found at %s", galaxy_file)
        return None, None
    except (OSError, yaml.YAMLError, MoleculeError) as exc:
        LOG.warning("Failed to load galaxy.yml at %s: %s", galaxy_file, exc)
        return None, None
    else:
        LOG.debug("Found galaxy.yml at %s", galaxy_file)
        return cwd, galaxy_data


@cache
def get_effective_molecule_glob() -> str:
    """Get the appropriate glob pattern.

    Returns:
        Glob pattern string for finding molecule.yml files.
        Returns MOLECULE_COLLECTION_GLOB if in collection,
        otherwise returns MOLECULE_GLOB.
    """
    # User provided
    if "MOLECULE_GLOB" in os.environ:
        return os.environ["MOLECULE_GLOB"]

    # No collection detected
    collection_dir, collection_data = get_collection_metadata()
    if not collection_dir or not collection_data:
        return MOLECULE_GLOB

    # Molecule found in root of collection
    if (Path.cwd() / MOLECULE_ROOT).exists():
        msg = f"Molecule scenarios should migrate to '{MOLECULE_COLLECTION_ROOT}'"
        LOG.warning(msg)
        return MOLECULE_GLOB

    # Molecule not found in collection use extensions
    msg = f"Collection '{collection_data['namespace']}.{collection_data['name']}' detected."
    LOG.info(msg)
    msg = f"Scenarios will be used from '{MOLECULE_COLLECTION_ROOT}'"
    LOG.info(msg)
    return MOLECULE_COLLECTION_GLOB


def to_bool(a: object) -> bool:
    """Return a bool for the arg.

    Args:
        a: A value to coerce to bool.

    Returns:
        A bool representation of a.
    """
    if a is None or isinstance(a, bool):
        return bool(a)
    if isinstance(a, str):
        a = a.lower()
    return a in ("yes", "on", "1", "true", 1)
