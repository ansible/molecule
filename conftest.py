"""PyTest Config File."""

from __future__ import print_function
import os
import pytest
import sys

pytest_plugins = ['helpers_namespace']


@pytest.fixture(scope="session", autouse=True)
def environ():
    """Configure default environment for tests."""
    # disable use of .netrc file to avoid galaxy-install errors with:
    # [ERROR]: failed to download the file: HTTP Error 401: Unauthorized
    # https://github.com/ansible/ansible/issues/61666
    os.environ['NETRC'] = ''

    # adds extra environment variables that may be needed during testing
    if not os.environ.get('TEST_BASE_IMAGE', ""):
        os.environ['TEST_BASE_IMAGE'] = 'docker.io/pycontribs/centos:7'


@pytest.hookimpl(hookwrapper=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Assure passed test match PYTEST_REQPASS value.

    Assures that pytest returns an error code when the number of expected passed
    tests does not match the PYTEST_REQPASS value.  When not defined or zero
    that functionality is ignored.
    """
    yield
    req_passed = int(os.environ.get('PYTEST_REQPASS', '0'))
    if req_passed and not config.option.collectonly:
        passed = 0
        for x in terminalreporter.stats.get('passed', []):
            if x.when == 'call' and x.outcome == 'passed':
                passed += 1
        if passed != req_passed:
            print(
                'ERROR: {} passed test but expected number was {}. '
                ' If that is expected please update PYTEST_REQPASS value for the failed job in zuul.d/layout.yaml file.'.format(
                    passed, req_passed
                ),
                file=sys.stderr,
            )
            sys.exit(127)
