import pluggy
from importlib import import_module
from molecule import logger
from molecule.util import lru_cache
import traceback

LOG = logger.get_logger(__name__)


CORE_DRIVERS = [
    "delegated",
    "digitalocean",
    "docker",
    "ec2",
    "gce",
    "hetznercloud",
    "linode",
    "lxc",
    "lxd",
    "openstack",
    "podman",
    "vagrant",
]


@lru_cache()
def molecule_drivers(as_dict=False, config=None):
    plugins = {}
    pm = pluggy.PluginManager("molecule_driver")
    for driver in CORE_DRIVERS:
        pm.register(import_module("molecule.driver.%s" % driver), name=driver)
    try:
        pm.load_setuptools_entrypoints("molecule_driver")
    except Exception:
        # These are not fatal because a broken driver should not make the entire
        # tool unusable.
        LOG.error("Failed to load driver entry points %s", traceback.format_exc())
    for p in pm.get_plugins():
        try:
            plugins[pm.get_name(p)] = p.load(config)
        except Exception as e:
            LOG.error("Failed to load %s driver: %s", pm.get_name(p), str(e))

    if as_dict:
        return plugins
    else:
        return sorted(list(plugins.keys()))
