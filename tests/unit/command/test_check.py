#  Copyright (c) 2015-2018 Cisco Systems, Inc.  # noqa: D100
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

import logging

from typing import TYPE_CHECKING

import pytest

from molecule.command import check


if TYPE_CHECKING:
    from unittest.mock import MagicMock, Mock

    from pytest_mock import MockerFixture

    from molecule import config


@pytest.fixture
def _patched_ansible_check(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("molecule.provisioner.ansible.Ansible.check")


# NOTE(retr0h): The use of the `patched_config_validate` fixture, disables
# config.Config._validate from executing.  Thus preventing odd side-effects
# throughout patched.assert_called unit tests.
def test_check_execute(  # noqa: D103
    mocker: MockerFixture,
    caplog: pytest.LogCaptureFixture,
    _patched_ansible_check: Mock,  # noqa: PT019
    patched_config_validate: Mock,
    config_instance: config.Config,
) -> None:
    config_instance.action = "check"
    c = check.Check(config_instance)

    with caplog.at_level(logging.INFO):
        c.execute()

    expected_record_count = 2
    assert len(caplog.records) == expected_record_count
    expected_message = "INFO     [default > check] Completed: Successful"
    assert caplog.records[1].getMessage() == expected_message

    _patched_ansible_check.assert_called_once_with()
