import os

import testinfra.utils.ansible_runner

inventory = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '.molecule',
    'ansible_inventory')
testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    inventory).get_hosts('bar')


def test_hostname(SystemInfo):
    assert 'instance-1' == SystemInfo.hostname
