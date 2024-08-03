"""Molecule API Module."""

import logging
import traceback

from collections import OrderedDict
from collections.abc import Hashable
from typing import Any, TypeVar

import pluggy

from ansible_compat.ports import cache

from molecule.driver.base import Driver
from molecule.verifier.base import Verifier


LOG = logging.getLogger(__name__)
K = TypeVar("K", bound=Hashable)


class MoleculeRuntimeWarning(RuntimeWarning):
    """A runtime warning used by Molecule and its plugins."""


class IncompatibleMoleculeRuntimeWarning(MoleculeRuntimeWarning):
    """A warning noting an unsupported runtime environment."""


@cache
def drivers(config: Any | None = None) -> dict[str, Driver]:  # noqa: ANN401
    """Return list of active drivers.

    Args:
        config: plugin config
    """
    plugins = OrderedDict()
    pm = pluggy.PluginManager("molecule.driver")
    try:
        pm.load_setuptools_entrypoints("molecule.driver")
    except (Exception, SystemExit):
        # These are not fatal because a broken driver should not make the entire
        # tool unusable.
        LOG.error("Failed to load driver entry point %s", traceback.format_exc())  # noqa: TRY400
    for plugin in pm.get_plugins():
        if issubclass(plugin, Driver):
            try:
                driver = plugin(config)
                plugins[driver.name] = driver
            except (Exception, SystemExit, TypeError) as e:
                LOG.error(  # noqa: TRY400
                    "Failed to load %s driver: %s",
                    pm.get_name(plugin),
                    str(e),
                )
        else:
            msg = f"Skipped loading plugin class {plugin} because is not a subclass of Driver."
            LOG.error(msg)

    return plugins


@cache
def verifiers(config=None) -> dict[str, Verifier]:  # type: ignore[no-untyped-def]  # noqa: ANN001
    """Return list of active verifiers."""
    plugins = OrderedDict()
    pm = pluggy.PluginManager("molecule.verifier")
    try:
        pm.load_setuptools_entrypoints("molecule.verifier")
    except Exception:  # noqa: BLE001
        # These are not fatal because a broken verifier should not make the entire
        # tool unusable.
        LOG.error("Failed to load verifier entry point %s", traceback.format_exc())  # noqa: TRY400
    for plugin_class in pm.get_plugins():
        try:
            if issubclass(plugin_class, Verifier):
                plugin = plugin_class(config)
                plugins[plugin.name] = plugin
        except Exception as e:  # noqa: BLE001, PERF203
            LOG.error("Failed to load %s driver: %s", pm.get_name(plugin), str(e))  # noqa: TRY400
    return plugins


__all__ = (
    "Driver",
    "IncompatibleMoleculeRuntimeWarning",
    "MoleculeRuntimeWarning",
    "Verifier",
    "drivers",
    "verifiers",
)
