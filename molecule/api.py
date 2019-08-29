import pkg_resources
from molecule.util import memoize


@memoize
def molecule_drivers(as_dict=False):

    plugins = {
        entry_point.name: entry_point.load()
        for entry_point in pkg_resources.iter_entry_points('molecule_driver')
    }
    if as_dict:
        return plugins
    else:
        return list(plugins.keys())
