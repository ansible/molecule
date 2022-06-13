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
"""Ansible-Playbook Provisioner Module."""

import logging
import warnings

from molecule import util
from molecule.api import MoleculeRuntimeWarning

LOG = logging.getLogger(__name__)


class AnsiblePlaybook(object):
    """Provisioner Playbook."""

    def __init__(self, playbook, config, verify=False):
        """
        Set up the requirements to execute ``ansible-playbook`` and returns \
        None.

        :param playbook: A string containing the path to the playbook.
        :param config: An instance of a Molecule config.
        :param verify: An optional bool to toggle the Plabook mode between
         provision and verify. False: provision; True: verify. Default is False.
        :returns: None
        """
        self._ansible_command = None
        self._playbook = playbook
        self._config = config
        self._cli = {}
        if verify:
            self._env = util.merge_dicts(
                self._config.verifier.env, self._config.config["verifier"]["env"]
            )
        else:
            self._env = self._config.provisioner.env

    def bake(self):
        """
        Bake an ``ansible-playbook`` command so it's ready to execute and \
        returns ``None``.

        :return: None
        """
        if not self._playbook:
            return

        # Pass a directory as inventory to let Ansible merge the multiple
        # inventory sources located under
        self.add_cli_arg("inventory", self._config.provisioner.inventory_directory)
        options = util.merge_dicts(self._config.provisioner.options, self._cli)
        verbose_flag = util.verbose_flag(options)
        if self._playbook != self._config.provisioner.playbooks.converge:
            if options.get("become"):
                del options["become"]

        # We do not pass user-specified Ansible arguments to the create and
        # destroy invocations because playbooks involved in those two
        # operations are not always provided by end users. And in those cases,
        # custom Ansible arguments can break the creation and destruction
        # processes.
        #
        # If users need to modify the creation of deletion, they can supply
        # custom playbooks and specify them in the scenario configuration.
        if self._config.action not in ["create", "destroy"]:
            ansible_args = list(self._config.provisioner.ansible_args) + list(
                self._config.ansible_args
            )
        else:
            ansible_args = []

        self._ansible_command = util.BakedCommand(
            cmd=[
                "ansible-playbook",
                *util.dict2args(options),
                *util.bool2args(verbose_flag),
                *ansible_args,
                self._playbook,  # must always go last
            ],
            cwd=self._config.scenario.directory,
            env=self._env,
        )

    def execute(self, action_args=None):
        """
        Execute ``ansible-playbook`` and returns a string.

        :return: str
        """
        if self._ansible_command is None:
            self.bake()

        if not self._playbook:
            LOG.warning("Skipping, %s action has no playbook.", self._config.action)
            return

        with warnings.catch_warnings(record=True) as warns:
            warnings.filterwarnings("default", category=MoleculeRuntimeWarning)
            self._config.driver.sanity_checks()
            result = util.run_command(self._ansible_command, debug=self._config.debug)

        if result.returncode != 0:
            util.sysexit_with_message(
                f"Ansible return code was {result.returncode}, command was: {result.args}",
                result.returncode,
                warns=warns,
            )

        return result.stdout

    def add_cli_arg(self, name, value):
        """
        Add argument to CLI passed to ansible-playbook and returns None.

        :param name: A string containing the name of argument to be added.
        :param value: The value of argument to be added.
        :return: None
        """
        if value:
            self._cli[name] = value

    def add_env_arg(self, name, value):
        """
        Add argument to environment passed to ansible-playbook and returns \
        None.

        :param name: A string containing the name of argument to be added.
        :param value: The value of argument to be added.
        :return: None
        """
        self._env[name] = value
