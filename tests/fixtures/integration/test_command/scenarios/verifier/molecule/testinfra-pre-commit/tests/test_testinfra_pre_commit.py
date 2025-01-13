"""Testinfra tests."""  # noqa: INP001

from __future__ import annotations


def test_ansible_hostname(host):  # type: ignore[no-untyped-def]  # noqa: ANN201
    """Validate hostname."""
    f = host.file("/tmp/molecule/instance-1")  # noqa: S108
    assert not f.exists
