"""PyTest Config File."""

from __future__ import print_function

import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def environ():
    """Configure default environment for tests."""
    # disable use of .netrc file to avoid galaxy-install errors with:
    # [ERROR]: failed to download the file: HTTP Error 401: Unauthorized
    # https://github.com/ansible/ansible/issues/61666
    os.environ["NETRC"] = ""

    # adds extra environment variables that may be needed during testing
    if not os.environ.get("TEST_BASE_IMAGE", ""):
        os.environ["TEST_BASE_IMAGE"] = "quay.io/centos/centos:stream8"
