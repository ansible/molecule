"""Testinfra tests."""  # noqa: INP001

import os

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"],
).get_hosts("all")


def test_side_effect_removed_file(host):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201
    """Validate that file was removed."""
    assert not host.file("/tmp/testfile").exists  # noqa: S108
