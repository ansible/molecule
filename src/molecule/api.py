"""Molecule API Module."""

from __future__ import annotations

import logging
import traceback

from collections import UserList
from typing import Any

import pluggy

from ansible_compat.ports import cache

from molecule.driver.base import Driver  # noqa: F401
from molecule.verifier.base import Verifier  # noqa: F401


LOG = logging.getLogger(__name__)


class UserListMap(UserList):  # type: ignore[type-arg]
    """A list where you can also access elements by their name.

    Example:
    -------
    foo['boo']
    foo.boo
    """

    def __getitem__(self, i):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN204
        """Implement indexing."""
        if isinstance(i, int):
            return super().__getitem__(i)
        return self.__dict__[i]

    def get(self, key, default):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D102
        return self.__dict__.get(key, default)

    def append(self, item) -> None:  # type: ignore[no-untyped-def]  # noqa: ANN001, D102
        self.__dict__[str(item)] = item
        super().append(item)


class MoleculeRuntimeWarning(RuntimeWarning):
    """A runtime warning used by Molecule and its plugins."""


class IncompatibleMoleculeRuntimeWarning(MoleculeRuntimeWarning):
    """A warning noting an unsupported runtime environment."""


@cache
def drivers(config: Any | None = None) -> UserListMap:  # noqa: ANN401
    """Return list of active drivers.

    Args:
        config: plugin config
    """
    plugins = UserListMap()
    pm = pluggy.PluginManager("molecule.driver")
    try:
        pm.load_setuptools_entrypoints("molecule.driver")
    except (Exception, SystemExit):
        # These are not fatal because a broken driver should not make the entire
        # tool unusable.
        LOG.error("Failed to load driver entry point %s", traceback.format_exc())  # noqa: TRY400
    for p in pm.get_plugins():
        try:
            plugins.append(p(config))
        except (Exception, SystemExit) as e:  # noqa: PERF203
            LOG.error("Failed to load %s driver: %s", pm.get_name(p), str(e))  # noqa: TRY400
    plugins.sort()
    return plugins


@cache
def verifiers(config=None) -> UserListMap:  # type: ignore[no-untyped-def]  # noqa: ANN001
    """Return list of active verifiers."""
    plugins = UserListMap()
    pm = pluggy.PluginManager("molecule.verifier")
    try:
        pm.load_setuptools_entrypoints("molecule.verifier")
    except Exception:  # noqa: BLE001
        # These are not fatal because a broken verifier should not make the entire
        # tool unusable.
        LOG.error("Failed to load verifier entry point %s", traceback.format_exc())  # noqa: TRY400
    for p in pm.get_plugins():
        try:
            plugins.append(p(config))
        except Exception as e:  # noqa: BLE001, PERF203
            LOG.error("Failed to load %s driver: %s", pm.get_name(p), str(e))  # noqa: TRY400
    plugins.sort()
    return plugins
