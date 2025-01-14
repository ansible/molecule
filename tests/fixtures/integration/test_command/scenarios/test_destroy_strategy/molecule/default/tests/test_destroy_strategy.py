"""Testinfra tests."""  # noqa: INP001

from __future__ import annotations

import os

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"],
).get_hosts("all")


def test_hostname(host):  # type: ignore[no-untyped-def]  # noqa: ANN201
    """Validate hostname."""
    assert host.check_output("hostname -s") == "instance"


def test_etc_molecule_directory(host):  # type: ignore[no-untyped-def]  # noqa: ANN201
    """Validate molecule directory."""
    f = host.file("/etc/molecule")

    assert f.is_directory
    assert f.user == "root"
    assert f.group == "root"
    assert f.mode == 0o755  # noqa: PLR2004


def test_etc_molecule_ansible_hostname_file(host):  # type: ignore[no-untyped-def]  # noqa: ANN201
    """Validate molecule instance file."""
    f = host.file("/etc/molecule/instance")

    assert f.is_file
    assert f.user == "root"
    assert f.group == "root"
    assert f.mode == 0o644  # noqa: PLR2004
