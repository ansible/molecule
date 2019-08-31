from molecule.driver.base import Base
from molecule.api import molecule_drivers


def looks_iterable(a):
    try:
        (x for x in a)
        return True
    except TypeError:
        return False


def test_api_molecule_drivers():

    # check if call without parameters returns a list of strings
    results = molecule_drivers()
    # print(results)
    assert looks_iterable(results)
    # delegated driver is expected to always be present
    assert 'delegated' in results


def test_api_molecule_drivers_as_dict():

    # check that with as_dict it will return a dictionary of driver instances
    results = molecule_drivers(as_dict=True)

    assert looks_iterable(results)

    # delegated driver is expected to always be present
    assert 'delegated' in results

    for driver in results.values():
        assert isinstance(driver, Base)
