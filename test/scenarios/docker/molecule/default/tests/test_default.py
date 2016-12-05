import os

import testinfra.utils.ansible_runner

inventory = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '.molecule',
    'ansible_inventory')
testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    inventory).get_hosts('all')


def test_etc_hosts(File):
    f = File('/etc/hosts')

    assert f.is_file
    assert f.user == 'root'
    assert f.group == 'root'
