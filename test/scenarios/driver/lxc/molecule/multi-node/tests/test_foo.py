import re

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory.yml').get_hosts('foo')


def test_hostname(SystemInfo):
    assert re.search(r'instance-[12]-multi-node', SystemInfo.hostname)
