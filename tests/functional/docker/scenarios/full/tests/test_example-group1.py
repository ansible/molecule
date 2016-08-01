import pytest

testinfra_hosts = ['example-group1']

pytestmark = pytest.mark.skip(reason=(
    'Cannot target hosts/groups '
    'https://github.com/metacloud/molecule/issues/300'))


def test_etc_molecule_example_group1(File):
    f = File('/etc/molecule/example-group1')

    assert f.is_file
    assert f.user == 'root'
    assert f.group == 'root'
    assert f.mode == 0o644
    assert f.contains('molecule example-group1 file')


def test_etc_molecule_example_group2(File):
    f = File('/etc/molecule/example-group2')

    assert not f.exists
