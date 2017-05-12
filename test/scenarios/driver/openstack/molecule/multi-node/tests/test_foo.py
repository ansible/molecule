import os
import re

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('foo')


def test_hostname(SystemInfo):
    assert re.search(r'instance-[12]-multi-node', SystemInfo.hostname)


def test_etc_molecule_directory(File):
    f = File('/etc/molecule')

    assert f.is_directory
    assert f.user == 'root'
    assert f.group == 'root'
    assert f.mode == 0o755


def test_etc_molecule_ansible_hostname_file(SystemInfo, File):
    filename = '/etc/molecule/{}'.format(SystemInfo.hostname)
    f = File(filename)

    assert f.is_file
    assert f.user == 'root'
    assert f.group == 'root'
    assert f.mode == 0o644
