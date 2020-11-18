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
#  DEALINGS IN THE SOFTWARE.
"""Molecule Shell Module."""
import os
import sys

import click
import click_completion
import pkg_resources

import molecule
from molecule import command
from molecule.api import drivers
from molecule.command.base import click_group_ex
from molecule.config import MOLECULE_DEBUG, MOLECULE_VERBOSITY, ansible_version
from molecule.console import console
from molecule.util import lookup_config_file

click_completion.init()

LOCAL_CONFIG_SEARCH = ".config/molecule/config.yml"
LOCAL_CONFIG = lookup_config_file(LOCAL_CONFIG_SEARCH)

ENV_FILE = ".env.yml"


def print_version(ctx, param, value):
    """Print version information."""
    if not value or ctx.resilient_parsing:
        return

    v = pkg_resources.parse_version(molecule.__version__)
    color = "bright_yellow" if v.is_prerelease else "green"
    msg = f"molecule [{color}]{v}[/] using python [repr.number]{sys.version_info[0]}.{sys.version_info[1]}[/] \n"

    msg += (
        f"    [repr.attrib_name]ansible[/][dim]:[/][repr.number]{ansible_version()}[/]"
    )
    for driver in drivers():
        msg += f"\n    [repr.attrib_name]{str(driver)}[/][dim]:[/][repr.number]{driver.version}[/][dim] from {driver.module}[/]"
    console.print(msg)

    ctx.exit()


@click_group_ex()  # type: ignore
@click.option(
    "--debug/--no-debug",
    default=MOLECULE_DEBUG,
    help="Enable or disable debug mode. Default is disabled.",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=MOLECULE_VERBOSITY,
    help="Increase Ansible verbosity level. Default is 0.",
)
@click.option(
    "--base-config",
    "-c",
    default=LOCAL_CONFIG,
    help=(
        "Path to a base config.  If provided Molecule will load "
        "this config first, and deep merge each scenario's "
        "molecule.yml on top. By default Molecule is looking for "
        "'{}' "
        "in current VCS repository and if not found it will look "
        "in user home. ({})"
    ).format(LOCAL_CONFIG_SEARCH, LOCAL_CONFIG),
)
@click.option(
    "--env-file",
    "-e",
    default=ENV_FILE,
    help=("The file to read variables from when rendering molecule.yml. " "(.env.yml)"),
)
@click.option(
    "--version", is_flag=True, callback=print_version, expose_value=False, is_eager=True
)
@click.pass_context
def main(ctx, debug, verbose, base_config, env_file):  # pragma: no cover
    """
    Molecule aids in the development and testing of Ansible roles.

    Enable autocomplete issue:

      eval "$(_MOLECULE_COMPLETE=source molecule)"
    """
    ctx.obj = {}
    ctx.obj["args"] = {}
    ctx.obj["args"]["debug"] = debug
    ctx.obj["args"]["verbose"] = verbose
    ctx.obj["args"]["base_config"] = base_config
    ctx.obj["args"]["env_file"] = env_file

    if verbose:
        os.environ["ANSIBLE_VERBOSITY"] = str(verbose)


# runtime environment checks to avoid delayed failures
if sys.version_info[0] > 2:
    try:
        if pkg_resources.get_distribution("futures"):
            raise SystemExit(
                "FATAL: futures package found, this package should not be installed in a Python 3 environment, please remove it. See https://github.com/agronholm/pythonfutures/issues/90"
            )
    except pkg_resources.DistributionNotFound:
        pass

main.add_command(command.cleanup.cleanup)
main.add_command(command.check.check)
main.add_command(command.converge.converge)
main.add_command(command.create.create)
main.add_command(command.dependency.dependency)
main.add_command(command.destroy.destroy)
main.add_command(command.drivers.drivers)
main.add_command(command.idempotence.idempotence)
main.add_command(command.init.init)
main.add_command(command.lint.lint)
main.add_command(command.list.list)
main.add_command(command.login.login)
main.add_command(command.matrix.matrix)
main.add_command(command.prepare.prepare)
main.add_command(command.reset.reset)
main.add_command(command.side_effect.side_effect)
main.add_command(command.syntax.syntax)
main.add_command(command.test.test)
main.add_command(command.verify.verify)
