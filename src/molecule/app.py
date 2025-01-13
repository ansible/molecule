"""Molecule Application Module."""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from ansible_compat.runtime import Runtime


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


@lru_cache
def get_app(path: Path) -> App:
    """Return the app instance.

    Args:
        path: The path to the project.

    Returns:
        App: The app instance.
    """
    return App(path)
