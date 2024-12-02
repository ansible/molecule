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
    """Galaxy is the default dependency manager.

    From v6.0.0, the dependencies are installed in the directory that defined
    in ansible configuration. The default installation directory is
    [DEFAULT_ROLES_PATH][]([ANSIBLE_HOME][]). If two versions of the same
    dependency is required, there is a conflict if the default installation
    directory is used because both are tried to be installed in one directory.

    Additional options can be passed to ``ansible-galaxy install`` through the
    options dict.  Any option set in this section will override the defaults.

    The `role-file` and `requirements-file` search path is `<role-name>`
    directory. The default value for `role-file` is `requirements.yml`, and the
    default value for `requirements-file` is `collections.yml`.

    1. If they are not defined in `options`, `molecule` will find them from the
    `<role-name>` directory, e.g. `<role-name>/requirements.yml` and
    `<role-name>/collections.yml`
    2. If they are defined in `options`, `molecule` will find them from
    `<role-name>/<the-value-of-role-file>` and
    `<role-name>/<the-value-of-requirements-file>`.

    !!! note

        Molecule will remove any options matching '^[v]+$', and pass ``-vvv``
        to the underlying ``ansible-galaxy`` command when executing
        `molecule --debug`.

    ``` yaml
        dependency:
          name: galaxy
          options:
            ignore-certs: True
            ignore-errors: True
            role-file: requirements.yml
            requirements-file: collections.yml
    ```

    Use "role-file" if you have roles only. Use the "requirements-file" if you
    need to install collections. Note that, with Ansible Galaxy's collections
    support, you can now combine the two lists into a single requirement if your
    file looks like this

    ``` yaml
        roles:
          - dep.role1
          - dep.role2
        collections:
          - ns.collection
          - ns2.collection2
    ```

    If you want to combine them, then just point your ``role-file`` and
    ``requirements-file`` to the same path. This is not done by default because
    older ``role-file`` only required a list of roles, while the collections
    must be under the ``collections:`` key within the file and pointing both to
    the same file by default could break existing code.

    The dependency manager can be disabled by setting ``enabled`` to False.

    ``` yaml
        dependency:
          name: galaxy
          enabled: False
    ```

    Environment variables can be passed to the dependency.

    ``` yaml
        dependency:
          name: galaxy
          env:
            FOO: bar
    ```

    [DEFAULT_ROLES_PATH]: https://docs.ansible.com/ansible/latest/cli/ansible-galaxy.html#cmdoption-ansible-galaxy-role-remove-p
    [ANSIBLE_HOME]: https://docs.ansible.com/ansible/latest/reference_appendices/config.html#ansible-home
    """

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
