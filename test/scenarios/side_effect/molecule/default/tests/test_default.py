import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_ntpd_is_not_running(host):
    service = host.service('ntpd')

    assert not service.is_running
    assert service.is_enabled
