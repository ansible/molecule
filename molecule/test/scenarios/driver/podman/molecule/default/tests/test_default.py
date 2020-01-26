import re
import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_hostname(host):
    """Validate hostname."""
    assert re.search(r'instance.*', host.check_output('hostname -s'))


def test_etc_molecule_directory(host):
    """Validate /etc/molecule directory."""
    f = host.file('/etc/molecule')

    assert f.is_directory
    assert f.user == 'root'
    assert f.group == 'root'
    assert f.mode == 0o755


def test_etc_molecule_ansible_hostname_file(host):
    """Validates /etc/molecule/{hostname}."""
    f = host.file('/etc/molecule/{}'.format(host.check_output('hostname -s')))

    assert f.is_file
    assert f.user == 'root'
    assert f.group == 'root'
    assert f.mode == 0o644


def test_buildarg_env_var(host):
    """Validates presenceof buildargs."""
    cmd_out = host.run("echo $envarg")
    assert cmd_out.stdout.strip() == 'this_is_a_test'
