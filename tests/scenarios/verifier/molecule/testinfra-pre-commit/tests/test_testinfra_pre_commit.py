"""Testinfra tests."""  # noqa: INP001


def test_ansible_hostname(host):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201
    """Validate hostname."""
    f = host.file("/tmp/molecule/instance-1")  # noqa: S108
    assert not f.exists
