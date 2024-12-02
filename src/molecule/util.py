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
from subprocess import CalledProcessError, CompletedProcess
from typing import TYPE_CHECKING, overload

import jinja2
import yaml

from ansible_compat.ports import cache
from rich.syntax import Syntax

from molecule.app import app
from molecule.console import console
from molecule.constants import MOLECULE_HEADER


if TYPE_CHECKING:
    from collections.abc import Generator, Iterable, MutableMapping
    from io import TextIOWrapper
    from typing import Any, AnyStr, NoReturn, TypeVar
    from warnings import WarningMessage

    from molecule.types import CommandArgs, ConfigData, Options, PlatformData

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


def print_debug(title: str, data: str) -> None:
    """Print debug information.

    Args:
        title: A title to describe the data.
        data: The data to print.
    """
    console.print(f"DEBUG: {title}:\n{data}")


def print_environment_vars(env: dict[str, str] | None) -> None:
    """Print ``Ansible`` and ``Molecule`` environment variables and returns None.

    Args:
        env: A dict containing the shell's environment as collected by ``os.environ``.
    """
    if env:
        ansible_env = {k: v for (k, v) in env.items() if "ANSIBLE_" in k}
        print_debug("ANSIBLE ENVIRONMENT", safe_dump(ansible_env, explicit_start=False))

        molecule_env = {k: v for (k, v) in env.items() if "MOLECULE_" in k}
        print_debug(
            "MOLECULE ENVIRONMENT",
            safe_dump(molecule_env, explicit_start=False),
        )

        combined_env = ansible_env.copy()
        combined_env.update(molecule_env)
        print_debug(
            "SHELL REPLAY",
            " ".join([f"{k}={v}" for (k, v) in sorted(combined_env.items())]),
        )
        print()  # noqa: T201


def do_report() -> None:
    """Dump html report atexit."""
    report_file = Path(os.environ["MOLECULE_REPORT"])
    LOG.info("Writing %s report.", report_file)
    with report_file.open("w") as f:
        f.write(console.export_html())
        f.close()


def sysexit(code: int = 1) -> NoReturn:
    """Perform a system exit with given code.

    Args:
        code: The return code to emit.
    """
    sys.exit(code)


def sysexit_with_message(
    msg: str,
    code: int = 1,
    detail: MutableMapping[str, Any] | None = None,
    warns: Iterable[WarningMessage] = (),
) -> NoReturn:
    """Exit with an error message.

    Args:
        msg: The message to display.
        code: The return code to exit with.
        detail: A potentially complex object that will be displayed alongside msg.
        warns: A series of warnings to send alongside the message.
    """
    # detail is usually a multi-line string which is not suitable for normal
    # logger.
    if detail:
        detail_str = safe_dump(detail) if isinstance(detail, dict) else str(detail)
        print(detail_str)  # noqa: T201
    LOG.critical(msg, extra={"highlighter": False})

    for warn in warns:
        LOG.warning(warn.__dict__["message"].args[0])
    sysexit(code)


def run_command(  # noqa: PLR0913
    cmd: str | list[str],
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
    *,
    debug: bool = False,
    echo: bool = False,  # noqa: ARG001
    quiet: bool = False,  # noqa: ARG001
    check: bool = False,
) -> CompletedProcess[str]:
    """Execute the given command and returns None.

    Args:
        cmd: A list of strings containing the command to run.
        env: A dict containing the shell's environment.
        cwd: An optional Path to the working directory.
        debug: An optional bool to toggle debug output.
        echo: An optional bool to toggle command echo.
        quiet: An optional bool to toggle command output.
        check: An optional bool to toggle command error checking.

    Returns:
        A completed process object.

    Raises:
        CalledProcessError: If return code is nonzero and check is True.
    """
    if debug:
        print_environment_vars(env)

    result = app.runtime.run(
        args=cmd,
        env=env,
        cwd=cwd,
        tee=True,
        set_acp=False,
    )
    if result.returncode != 0 and check:
        raise CalledProcessError(
            returncode=result.returncode,
            cmd=result.args,
            output=result.stdout,
            stderr=result.stderr,
        )
    return result


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
    """
    try:
        return yaml.safe_load(string) or {}
    except yaml.scanner.ScannerError as e:
        sysexit_with_message(str(e))
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
    return {k: options[k] for k in options if not re.match("^[v]+$", k)}


@overload
def abs_path(path: Path) -> Path: ...


@overload
def abs_path(path: str | None) -> str: ...


def abs_path(path: str | Path | None) -> str | Path:
    """Return absolute path.

    Args:
        path: File path to resolve absolute path from.

    Returns:
        Absolute path of path.
    """
    if not path:
        return ""

    output_type = type(path)
    if isinstance(path, str):
        path = Path(path)
    path = path.resolve()

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
    """
    if cmd_args.get("parallel") and cmd_args.get("destroy") == "never":
        msg = 'Combining "--parallel" and "--destroy=never" is not supported'
        sysexit_with_message(msg)


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
        filename: Config file name to find.and

    Returns:
        Path to config file or None if not found.
    """
    for path in [find_vcs_root(default="~"), "~"]:
        f = (Path(path) / filename).expanduser()
        if f.is_file():
            LOG.info("Found config file %s", f)
            return str(f)
    return None


def boolean(value: bool | AnyStr, *, strict: bool = True) -> bool:
    """Evaluate any object as boolean matching ansible behavior.

    Args:
        value: The value to evaluate as a boolean.
        strict: If True, invalid booleans will raises TypeError instead of returning False.

    Returns:
        The boolean value of value.

    Raises:
        TypeError: If value does not resolve to a valid boolean and strict is True.
    """
    # Based on https://github.com/ansible/ansible/blob/devel/lib/ansible/module_utils/parsing/convert_bool.py

    BOOLEANS_TRUE = frozenset(("y", "yes", "on", "1", "true", "t", 1, 1.0, True))  # noqa: N806
    BOOLEANS_FALSE = frozenset(("n", "no", "off", "0", "false", "f", 0, 0.0, False))  # noqa: N806
    BOOLEANS = BOOLEANS_TRUE.union(BOOLEANS_FALSE)  # noqa: N806

    if isinstance(value, bool):
        return value

    normalized_value = str(value).lower().strip()

    if normalized_value in BOOLEANS_TRUE:
        return True
    if normalized_value in BOOLEANS_FALSE or not strict:
        return False

    raise TypeError(  # noqa: TRY003
        f"The value '{value!s}' is not a valid boolean.  Valid booleans include: {', '.join(repr(i) for i in BOOLEANS)!s}",  # noqa: EM102, E501
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


def bool2args(data: bool | list[str]) -> list[str]:  # noqa: ARG001
    """Convert a boolean value to command line argument (flag).

    Args:
        data: A boolean value.

    Returns:
        An empty list
    """
    return []


def print_as_yaml(data: object) -> None:
    """Render python object as yaml on console.

    Args:
        data: A YAML object.
    """
    # https://github.com/Textualize/rich/discussions/990#discussioncomment-342217
    result = Syntax(code=safe_dump(data), lexer="yaml", background_color="default")
    console.print(result)
