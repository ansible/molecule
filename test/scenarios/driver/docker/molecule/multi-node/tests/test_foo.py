import os
import re

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('foo')


def test_hostname(SystemInfo):
    assert re.search(r'instance-[12]', SystemInfo.hostname)
