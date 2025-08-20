"""Base definition for Ansible Galaxy dependencies."""

from __future__ import annotations

from typing import TYPE_CHECKING

from molecule import util
from molecule.dependency.ansible_galaxy.collections import Collections
from molecule.dependency.ansible_galaxy.roles import Roles
from molecule.dependency.base import Base


if TYPE_CHECKING:
    from collections.abc import MutableMapping

    from molecule.config import Config


class AnsibleGalaxy(Base):
    """The Ansible Galaxy dependency."""

    def __init__(self, config: Config) -> None:
        """Construct AnsibleGalaxy.

        Args:
            config: Molecule Config instance.
        """
        super().__init__(config)
        self.invocations = [Roles(config), Collections(config)]

    def execute(self, action_args: list[str] | None = None) -> None:  # noqa: ARG002
        """Execute all Ansible Galaxy dependencies.

        Args:
            action_args: Arguments for invokers. Unused.
        """
        for invoker in self.invocations:
            invoker.execute()

    def _has_requirements_file(self) -> bool:
        has_file = False
        for invoker in self.invocations:
            has_file = has_file or invoker._has_requirements_file()  # noqa: SLF001
        return has_file

    @property
    def default_env(self) -> dict[str, str]:
        """Default environment variables across all invokers.

        Returns:
            Merged dictionary of default env vars for all invokers.
        """
        env: dict[str, str] = {}
        for invoker in self.invocations:
            env = util.merge_dicts(env, invoker.default_env)
        return env

    @property
    def default_options(self) -> MutableMapping[str, str | bool]:
        """Default options across all invokers.

        Returns:
            Merged dictionary of default options for all invokers.
        """
        opts: MutableMapping[str, str | bool] = {}
        for invoker in self.invocations:
            opts = util.merge_dicts(opts, invoker.default_options)
        return opts
