import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('example-group2')


def test_etc_molecule_example_group2(host):
    f = host.file('/etc/molecule/example-group2')

    assert f.is_file
    assert f.user == 'root'
    assert f.group == 'root'
    assert f.mode == 0o644
    assert f.contains('molecule example-group2 file')


def test_etc_molecule_example_group1(host):
    f = host.file('/etc/molecule/example-group1')

    assert not f.exists
