import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_hostname(host):
    assert 'instance' == host.check_output('hostname -s')


def test_etc_molecule_directory(host):
    f = host.file('/etc/molecule')

    assert f.is_directory
    assert f.user == 'root'
    assert f.group == 'root'
    assert f.mode == 0o755


def test_etc_molecule_ansible_hostname_file(host):
    f = host.file('/etc/molecule/instance')

    assert f.is_file
    assert f.user == 'root'
    assert f.group == 'root'
    assert f.mode == 0o644


def test_buildarg_env_var(host):
    cmd_out = host.run("echo $envarg")
    assert cmd_out.stdout.strip() == 'this_is_a_test'


def test_host_docker_network_interfaces(host):
    interface_count = 4
    interface_addresses = []

    for i in range(0, interface_count):
        interface = host.interface('eth{}'.format(i))
        assert interface.exists
        interface_addresses += interface.addresses

    assert len(filter(lambda addr: addr.startswith(
        '10.255.254.'), interface_addresses)) == 1
    assert len(filter(lambda addr: addr.startswith(
        '10.255.255.'), interface_addresses)) == 1
