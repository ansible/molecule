"""Molecule API Module."""

import logging
import traceback
from collections import UserList

import pluggy

from molecule.driver.base import Driver  # noqa
from molecule.util import lru_cache
from molecule.verifier.base import Verifier  # noqa

LOG = logging.getLogger(__name__)


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

    def append(self, item) -> None:
        self.__dict__[str(item)] = item
        super(UserListMap, self).append(item)


@lru_cache()
def drivers(config=None) -> UserListMap:
    """Return list of active drivers."""
    plugins = UserListMap()
    pm = pluggy.PluginManager("molecule.driver")
    try:
        pm.load_setuptools_entrypoints("molecule.driver")
    except (Exception, SystemExit):
        # These are not fatal because a broken driver should not make the entire
        # tool unusable.
        LOG.error("Failed to load driver entry point %s", traceback.format_exc())
    for p in pm.get_plugins():
        try:
            plugins.append(p(config))
        except (Exception, SystemExit) as e:
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
