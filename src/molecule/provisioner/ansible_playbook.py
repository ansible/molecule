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

from __future__ import annotations

import shlex
import subprocess
import warnings

from typing import TYPE_CHECKING

from rich.markup import escape

from molecule import logger, util
from molecule.api import MoleculeRuntimeWarning
from molecule.exceptions import ScenarioFailureError
from molecule.reporting import CompletionState


if TYPE_CHECKING:
    from molecule.config import Config


class AnsiblePlaybook:
    """Provisioner Playbook."""

    def __init__(
        self,
        playbook: str | None,
        config: Config,
        *,
        verify: bool = False,
    ) -> None:
        """Set up the requirements to execute ``ansible-playbook``.

        Args:
            playbook: A string containing the path to the playbook.
            config: An instance of a Molecule config.
            verify: An optional bool to toggle the Playbook mode between provision and verify.
                False provision; True: verify. Default is False.
        """
        self._ansible_command: list[str] = []
        self._playbook = playbook
        self._config = config
        self._cli: dict[str, str | bool] = {}
        self._env: dict[str, str] = {}
        if verify:
            self._env = util.merge_dicts(
                self._config.verifier.env,
                self._config.config["verifier"]["env"],
            )
        elif self._config.provisioner:
            self._env = self._config.provisioner.env

    @property
    def _log(self) -> logger.ScenarioLoggerAdapter:
        """Get a fresh scenario logger with current context.

        Returns:
            A scenario logger adapter with current scenario and step context.
        """
        # Get step context from the current action being executed
        step_name = getattr(self._config, "action", "provisioner")
        return logger.get_scenario_logger(__name__, self._config.scenario.name, step_name)

    def bake(self) -> None:
        """Bake ``ansible-playbook`` or ``navigator run`` command so it's ready to execute.

        Raises:
            ValueError: when backend is incorrect.
            RuntimeError: when ansible-playbook or ansible-navigator is not available.
        """
        if not self._playbook:
            return

        if self._config.provisioner:
            # Pass a directory as inventory to let Ansible merge the multiple
            # inventory sources located under
            self.add_cli_arg("inventory", self._config.provisioner.inventory_directory)
            options = util.merge_dicts(self._config.provisioner.options, self._cli)
            verbose_flag = util.verbose_flag(options)
            if self._playbook != self._config.provisioner.playbooks.converge:  # noqa: SIM102
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
                    self._config.ansible_args,
                )
            else:
                ansible_args = []

            backend = self._config.executor

            if backend:
                try:
                    result = subprocess.run(
                        [backend, "--version"],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    self._log.info("%s version: %s", backend, result.stdout.strip())
                except subprocess.CalledProcessError as exc:
                    msg = f"{backend} is not available. Please ensure that it is installed."
                    raise RuntimeError(msg) from exc

            if backend == "ansible-playbook":
                self._ansible_command = [
                    "ansible-playbook",
                    *util.dict2args(options),
                    *util.bool2args(verbose_flag),
                    *ansible_args,
                    self._playbook,  # must always go last
                ]

            elif backend == "ansible-navigator":
                self._ansible_command = [
                    "ansible-navigator",
                    "run",
                    self._playbook,
                    "--mode",
                    "stdout",
                    *util.dict2args(options),
                    *util.bool2args(verbose_flag),
                    *ansible_args,
                ]
            else:
                msg = f"Unsupported backend: {backend}"
                raise ValueError(msg)

    def execute(self, action_args: list[str] | None = None) -> str:  # noqa: ARG002
        """Execute ``ansible-playbook`` or ``ansible-navigator run``.

        Args:
            action_args: Arguments to forward to the action. Unused.

        Returns:
            Output from ansible-playbook or ansible-navigator.

        Raises:
            ScenarioFailureError: when Ansible returns nonzero code.
        """
        if not self._ansible_command:
            self.bake()

        if not self._playbook:
            message = "Missing playbook"
            note = f"Remove from {self._config.subcommand}_sequence to suppress"
            self._config.scenario.results.add_completion(
                CompletionState.missing(message=message, note=note),
            )
            return ""

        with warnings.catch_warnings(record=True) as warns:
            warnings.filterwarnings("default", category=MoleculeRuntimeWarning)
            self._config.driver.sanity_checks()
            cwd = self._config.scenario_path
            result = self._config.app.run_command(
                cmd=self._ansible_command,
                env=self._env,
                debug=self._config.debug,
                cwd=cwd,
            )

        if result.returncode != 0:
            err = f"Ansible return code was {result.returncode}, command was: [dim]{escape(shlex.join(result.args))}[/]"
            self._config.scenario.results.add_completion(CompletionState.failed(note=err))

            raise ScenarioFailureError(
                err,
                code=result.returncode,
                warns=warns,
            )

        self._config.scenario.results.add_completion(CompletionState.successful)
        return result.stdout

    def add_cli_arg(self, name: str, value: str | bool) -> None:  # noqa: FBT001
        """Add argument to CLI passed to ansible-playbook.

        Args:
            name: A string containing the name of argument to be added.
            value: The value of argument to be added.
        """
        if value:
            self._cli[name] = value

    def add_env_arg(self, name: str, value: str) -> None:
        """Add argument to environment passed to ansible-playbook.

        Args:
            name: A string containing the name of argument to be added.
            value: The value of argument to be added.
        """
        self._env[name] = value
