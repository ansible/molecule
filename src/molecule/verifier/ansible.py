#  Copyright (c) 2019 Red Hat, Inc.
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
"""Ansible Verifier Module."""

from __future__ import annotations

import os

from typing import TYPE_CHECKING, cast

from molecule import logger, util
from molecule.api import Verifier
from molecule.reporting import CompletionState


if TYPE_CHECKING:
    from collections.abc import MutableMapping

    from molecule.verifier.base import Schema


class Ansible(Verifier):
    """`Ansible`_ is the default test verifier.

    Molecule executes a playbook (`verify.yml`) located in the role's
    `scenario.directory`.

    ``` yaml
        verifier:
          name: ansible
    ```

    The testing can be disabled by setting ``enabled`` to False.

    ``` yaml
        verifier:
          name: ansible
          enabled: False
    ```

    Environment variables can be passed to the verifier.

    ``` yaml

        verifier:
          name: ansible
          env:
            FOO: bar
    ```
    """

    @property
    def _log(self) -> logger.ScenarioLoggerAdapter:
        """Get a fresh scenario logger with current context.

        Returns:
            A scenario logger adapter with current scenario and step context.
        """
        # Get step context from the current action being executed
        step_name = getattr(self._config, "action", "verify")
        scenario_name = self._config.scenario.name if self._config else "unknown"
        return logger.get_scenario_logger(__name__, scenario_name, step_name)

    @property
    def name(self) -> str:
        """Name of the verifier.

        Returns:
            The name of the verifier.
        """
        return "ansible"

    @property
    def default_options(self) -> MutableMapping[str, str | bool]:
        """Get default CLI arguments provided to ``cmd``.

        Returns:
            The default verifier options.
        """
        return {}

    @property
    def default_env(self) -> dict[str, str]:
        """Get default env variables provided to ``cmd``.

        Returns:
            The default verifier environment variables.
        """
        env = cast("dict[str, str]", os.environ)
        env = util.merge_dicts(env, self._config.env)
        if self._config.provisioner:
            env = util.merge_dicts(env, self._config.provisioner.env)
        return env

    def execute(self, action_args: list[str] | None = None) -> None:
        """Execute ``cmd``.

        Args:
            action_args: list of arguments to be passed.
        """
        if not self.enabled:
            msg = "Skipping, verifier is disabled."
            self._log.warning(msg)
            self._config.scenario.results.add_completion(CompletionState.disabled)
            return

        if self._config.provisioner:
            # Check if verify playbook exists before calling provisioner
            if not self._config.provisioner.playbooks.verify:
                note = f"Remove from {self._config.subcommand}_sequence to suppress"
                message = "Missing playbook"
                self._config.scenario.results.add_completion(
                    CompletionState.missing(message=message, note=note),
                )
                return

            self._config.provisioner.verify(action_args)

    def schema(self) -> Schema:
        """Return validation schema.

        Returns:
            Verifier schema.
        """
        return {
            "verifier": {
                "type": "dict",
                "schema": {"name": {"type": "string", "allowed": ["ansible"]}},
            },
        }
