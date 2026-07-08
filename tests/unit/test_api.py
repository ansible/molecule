#  Copyright (c) 2019 Red Hat, Inc.  # noqa: D100
#  Copyright (c) 2015-2018 Cisco Systems, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
from __future__ import annotations

from unittest.mock import MagicMock, patch

from molecule import api
from molecule.driver.base import Driver
from molecule.exceptions import MoleculeError
from molecule.verifier.base import Verifier


def test_api_drivers() -> None:  # noqa: D103
    results = api.drivers()

    for result in results.values():
        assert isinstance(result, api.Driver)

    assert "default" in results


def test_api_verifiers() -> None:  # noqa: D103
    x = ["testinfra", "ansible"]

    assert all(elem in api.verifiers() for elem in x)


def test_drivers_logs_exception_on_plugin_failure() -> None:
    """Drivers that raise MoleculeError or TypeError are logged and skipped."""

    class _BrokenDriver(Driver):
        def __init__(self, config: object = None) -> None:  # noqa: ARG002  # pylint: disable=super-init-not-called
            msg = "cannot initialize"
            raise MoleculeError(msg)

    mock_pm = MagicMock()
    mock_pm.get_plugins.return_value = [_BrokenDriver]
    mock_pm.get_name.return_value = "_BrokenDriver"

    with (
        patch("molecule.api.pluggy.PluginManager", return_value=mock_pm),
        patch("molecule.api.LOG") as mock_log,
    ):
        api.drivers.cache_clear()
        result = api.drivers.__wrapped__(None)

    assert result == {}
    mock_log.exception.assert_called_once()
    assert "_BrokenDriver" in mock_log.exception.call_args[0][1]


def test_verifiers_logs_exception_on_plugin_failure() -> None:
    """Verifiers that raise an exception are logged and skipped."""

    class _BrokenVerifier(Verifier):
        def __init__(self, config: object = None) -> None:  # noqa: ARG002  # pylint: disable=super-init-not-called
            msg = "boom"
            raise RuntimeError(msg)

    mock_pm = MagicMock()
    mock_pm.get_plugins.return_value = [_BrokenVerifier]

    with (
        patch("molecule.api.pluggy.PluginManager", return_value=mock_pm),
        patch("molecule.api.LOG") as mock_log,
    ):
        api.verifiers.cache_clear()
        result = api.verifiers.__wrapped__(None)

    assert result == {}
    mock_log.exception.assert_called_once()
    assert "_BrokenVerifier" in mock_log.exception.call_args[0][1]
