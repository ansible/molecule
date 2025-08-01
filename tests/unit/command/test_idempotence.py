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

from molecule.command import idempotence
from molecule.exceptions import ScenarioFailureError


if TYPE_CHECKING:
    from unittest.mock import Mock

    from pytest_mock import MockerFixture

    from molecule import config


@pytest.fixture
def _patched_is_idempotent(mocker: MockerFixture) -> Mock:
    return mocker.patch("molecule.command.idempotence.Idempotence._is_idempotent")


# NOTE(retr0h): The use of the `patched_config_validate` fixture, disables
# config.Config._validate from executing.  Thus preventing odd side-effects
# throughout patched.assert_called unit tests.
@pytest.fixture
def _instance(patched_config_validate, config_instance: config.Config):  # type: ignore[no-untyped-def]  # noqa: ANN202
    config_instance.state.change_state("converged", True)  # noqa: FBT003

    return idempotence.Idempotence(config_instance)


def test_idempotence_execute(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    mocker: MockerFixture,
    caplog: pytest.LogCaptureFixture,
    patched_ansible_converge,
    _patched_is_idempotent: Mock,  # noqa: PT019
    _instance,  # noqa: PT019
):
    _instance._config.action = "idempotence"
    i = idempotence.Idempotence(_instance._config)

    with caplog.at_level(logging.INFO):
        i.execute()

    expected_record_count = 2
    assert len(caplog.records) == expected_record_count
    expected_message = "INFO     [default > idempotence] Completed: Successful"
    assert caplog.records[1].getMessage() == expected_message

    patched_ansible_converge.assert_called_once_with()

    _patched_is_idempotent.assert_called_once_with("patched-ansible-converge-stdout")


def test_execute_raises_when_not_converged(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    caplog: pytest.LogCaptureFixture,
    patched_ansible_converge,
    _instance,  # noqa: PT019
):
    _instance._config.state.change_state("converged", False)  # noqa: FBT003
    with pytest.raises(ScenarioFailureError) as e:
        _instance.execute()

    assert e.value.code == 1

    msg = "Instances not converged.  Please converge instances first."
    assert msg in caplog.text


def test_execute_raises_when_fails_idempotence(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    mocker: MockerFixture,
    caplog: pytest.LogCaptureFixture,
    patched_ansible_converge,
    _patched_is_idempotent: Mock,  # noqa: PT019
    _instance,  # noqa: PT019
):
    _patched_is_idempotent.return_value = False
    with pytest.raises(ScenarioFailureError) as e:
        _instance.execute()

    assert e.value.code == 1

    msg = "Idempotence test failed because of the following tasks:\n"
    assert msg in caplog.text


def test_is_idempotent(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    output = """
PLAY RECAP ***********************************************************
check-command-01: ok=3    changed=0    unreachable=0    failed=0
    """

    assert _instance._is_idempotent(output)


def test_is_idempotent_not_idempotent(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    output = """
PLAY RECAP ***********************************************************
check-command-01: ok=2    changed=1    unreachable=0    failed=0
check-command-02: ok=2    changed=1    unreachable=0    failed=0
    """

    assert not _instance._is_idempotent(output)


def test_non_idempotent_tasks_idempotent(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    output = """
PLAY [all] ***********************************************************

GATHERING FACTS ******************************************************
ok: [check-command-01]

TASK: [Idempotence test] *********************************************
ok: [check-command-01]

PLAY RECAP ***********************************************************
check-command-01: ok=3    changed=0    unreachable=0    failed=0
"""
    result = _instance._non_idempotent_tasks(output)

    assert result == []


def test_non_idempotent_tasks_not_idempotent(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    output = """
PLAY [all] ***********************************************************

GATHERING FACTS ******************************************************
ok: [check-command-01]
ok: [check-command-02]

TASK: [Idempotence test] *********************************************
changed: [check-command-01]
changed: [check-command-02]

PLAY RECAP ***********************************************************
check-command-01: ok=2    changed=1    unreachable=0    failed=0
check-command-02: ok=2    changed=1    unreachable=0    failed=0
"""
    result = _instance._non_idempotent_tasks(output)

    assert result == [
        "* [check-command-01] => Idempotence test",
        "* [check-command-02] => Idempotence test",
    ]
