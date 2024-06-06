"""Testinfra tests."""


def test_ansible_hostname(host):  # type: ignore[no-untyped-def]
    """Validate hostname."""
    f = host.file("/tmp/molecule/instance-1")
    assert not f.exists
