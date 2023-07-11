"""Testinfra tests."""


def test_side_effect_removed_file(host):
    """Validate that file was removed."""
    assert not host.file("/tmp/testfile").exists
