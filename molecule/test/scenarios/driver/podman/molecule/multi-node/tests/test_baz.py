"""Testinfra tests."""

import os
import re

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("baz")


def test_hostname(host):
    """Validate hostname."""
    assert re.search(r"instance-2.*", host.check_output("hostname -s"))


def test_etc_molecule_directory(host):
    """Validate molecule directory."""
    f = host.file("/etc/molecule")

    assert f.is_directory
    assert f.user == "root"
    assert f.group == "root"
    assert f.mode == 0o755


def test_etc_molecule_ansible_hostname_file(host):
    """Validate molecule file."""
    f = host.file("/etc/molecule/{}".format(host.check_output("hostname -s")))

    assert f.is_file
    assert f.user == "root"
    assert f.group == "root"
    assert f.mode == 0o644
