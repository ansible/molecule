import pkg_resources
from molecule import logger


LOG = logger.get_logger(__name__)

try:
    from functools import lru_cache
except ImportError:
    from backports.functools_lru_cache import lru_cache


@lru_cache()
def molecule_drivers(as_dict=False):

    plugins = {}
    for entry_point in pkg_resources.iter_entry_points('molecule_driver'):
        try:
            plugins[entry_point.name] = entry_point.load()
        except Exception as e:
            LOG.error("Failed to load %s driver: %s", entry_point.name, str(e))

    if as_dict:
        return plugins
    else:
        return list(plugins.keys())
