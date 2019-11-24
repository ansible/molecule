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

import click
import os
import sys

from molecule import logger
from molecule.command import base
from molecule.provisioner.ansible_playbook import AnsiblePlaybook

if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess


LOG = logger.get_logger(__name__)


class Lint(base.Base):
    """
    .. program:: molecule lint

    .. option:: molecule lint

        Target the default scenario.

    .. program:: molecule lint --scenario-name foo

    .. option:: molecule lint --scenario-name foo

        Targeting a specific scenario.

    .. program:: molecule --debug lint

    .. option:: molecule --debug lint

        Executing with `debug`.

    .. program:: molecule --base-config base.yml lint

    .. option:: molecule --base-config base.yml lint

        Executing with a `base-config`.

    .. program:: molecule --env-file foo.yml lint

    .. option:: molecule --env-file foo.yml lint

        Load an env file to read variables from when rendering
        molecule.yml.
    """

    def execute(self):
        """
        Execute the actions necessary to perform a `molecule lint` and
        returns None.

        :return: None
        """

        lint_pb = os.path.join(self._config.molecule_directory, "lint.yml")
        if os.path.isfile(lint_pb):
            self.print_info("Using custom linting playbook {}".format(lint_pb))

            _instance = AnsiblePlaybook(playbook=lint_pb, config=self._config)
            _instance.bake()
            _instance.execute()
        else:
            self.print_info("Running: {}".format(self._config.lint['cmd']))
            r = subprocess.run(
                self._config.lint['cmd'],
                cwd=os.path.join(self._config.molecule_directory, ""),
                stderr=sys.stderr,
                stdout=sys.stdout,
                universal_newlines=True,
                shell=True,
            )
            if r.returncode:
                sys.exit(r.returncode)


@click.command()
@click.pass_context
@click.option(
    '--scenario-name',
    '-s',
    default=base.MOLECULE_DEFAULT_SCENARIO_NAME,
    help='Name of the scenario to target. ({})'.format(
        base.MOLECULE_DEFAULT_SCENARIO_NAME
    ),
)
def lint(ctx, scenario_name):  # pragma: no cover
    """ Lint the role (dependency, lint). """
    args = ctx.obj.get('args')
    subcommand = base._get_subcommand(__name__)
    command_args = {'subcommand': subcommand}

    base.execute_cmdline_scenarios(scenario_name, args, command_args)


# TODO(ssbarnea): Expand this to allow multiple linter templates
def map_lint_name_to_cmd(name):
    if name == 'yamllint':
        return 'yamllint .'
