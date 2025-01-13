"""Molecule Application Module."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from subprocess import CalledProcessError, CompletedProcess
from typing import TYPE_CHECKING

from ansible_compat.runtime import Runtime

from molecule.util import print_environment_vars


if TYPE_CHECKING:
    from pathlib import Path


class App:
    """App class that keep runtime status."""

    def __init__(self, path: Path) -> None:
        """Create a new app instance.

        Args:
            path: The path to the project.
        """
        self.runtime = Runtime(project_dir=path, isolated=False)

    def run_command(  # noqa: PLR0913
        self,
        cmd: str | list[str],
        env: dict[str, str] | None = None,
        cwd: Path | None = None,
        *,
        debug: bool = False,
        echo: bool = False,  # noqa: ARG002
        quiet: bool = False,  # noqa: ARG002
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

        result = self.runtime.run(
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


@lru_cache
def get_app(path: Path) -> App:
    """Return the app instance.

    Args:
        path: The path to the project.

    Returns:
        App: The app instance.
    """
    return App(path)
