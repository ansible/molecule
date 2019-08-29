import pkg_resources

try:
    from functools import lru_cache
except ImportError:
    from backports.functools_lru_cache import lru_cache


@lru_cache()
def molecule_drivers(as_dict=False):

    plugins = {
        entry_point.name: entry_point.load()
        for entry_point in pkg_resources.iter_entry_points('molecule_driver')
    }
    if as_dict:
        return plugins
    else:
        return list(plugins.keys())
