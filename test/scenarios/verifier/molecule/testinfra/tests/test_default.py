import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_ansible_hostname(host):
    f = host.file('/tmp/molecule/instance-1')

    assert not f.exists
