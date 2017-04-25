import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('baz')


def test_hostname(SystemInfo):
    assert 'instance-2-multi-node' == SystemInfo.hostname
