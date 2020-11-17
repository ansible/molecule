"""Molecule API Module."""

import traceback
from collections import UserList

import pluggy

from molecule import logger
from molecule.driver.base import Driver  # noqa
from molecule.util import lru_cache
from molecule.verifier.base import Verifier  # noqa

LOG = logger.get_logger(__name__)


class UserListMap(UserList):
    """A list where you can also access elements by their name.

    Example:
    foo['boo']
    foo.boo
    """

    def __getitem__(self, i):
        """Implement indexing."""
        if isinstance(i, int):
            return super(UserListMap, self).__getitem__(i)
        else:
            return self.__dict__[i]

    def get(self, key, default):
        return self.__dict__.get(key, default)

    def append(self, element) -> None:
        self.__dict__[str(element)] = element
        super(UserListMap, self).append(element)


@lru_cache()
def drivers(config=None) -> UserListMap:
    """Return list of active drivers."""
    plugins = UserListMap()
    pm = pluggy.PluginManager("molecule.driver")
    try:
        pm.load_setuptools_entrypoints("molecule.driver")
    except Exception:
        # These are not fatal because a broken driver should not make the entire
        # tool unusable.
        LOG.error("Failed to load driver entry point %s", traceback.format_exc())
    for p in pm.get_plugins():
        try:
            plugins.append(p(config))
        except Exception as e:
            LOG.error("Failed to load %s driver: %s", pm.get_name(p), str(e))
    plugins.sort()
    return plugins


@lru_cache()
def verifiers(config=None) -> UserListMap:
    """Return list of active verifiers."""
    plugins = UserListMap()
    pm = pluggy.PluginManager("molecule.verifier")
    try:
        pm.load_setuptools_entrypoints("molecule.verifier")
    except Exception:
        # These are not fatal because a broken verifier should not make the entire
        # tool unusable.
        LOG.error("Failed to load verifier entry point %s", traceback.format_exc())
    for p in pm.get_plugins():
        try:
            plugins.append(p(config))
        except Exception as e:
            LOG.error("Failed to load %s driver: %s", pm.get_name(p), str(e))
    plugins.sort()
    return plugins
