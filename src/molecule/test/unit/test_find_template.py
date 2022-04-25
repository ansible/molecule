import os

import pytest

from molecule.util import find_template


@pytest.fixture(params=["fake-repo-pre", "fake-repo-pre2"])
def repo_dir(request):
    """Fixture returning path for `test_find_template` test."""
    return os.path.join("src/molecule/test/unit", request.param)


def test_find_template(repo_dir):
    """Verify correctness of `find_template` path detection."""
    template = find_template(repo_dir=repo_dir)

    test_dir = os.path.join(repo_dir, "{{cookiecutter.repo_name}}")
    assert template == test_dir
