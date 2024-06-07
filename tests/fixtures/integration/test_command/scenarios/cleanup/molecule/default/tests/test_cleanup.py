"""Testinfra tests."""  # noqa: INP001

import os

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"],
).get_hosts("all")


def test_hosts_file(host):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201
    """Validate host file."""
    f = host.file("/etc/hosts")

    assert f.exists
    assert f.user == "root"
    assert f.group == "root"
