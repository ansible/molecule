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

import os

from typing import TYPE_CHECKING

import pytest

from molecule import config, util
from molecule.command import prepare


if TYPE_CHECKING:
    from unittest.mock import MagicMock, Mock

    from pytest_mock import MockerFixture


@pytest.fixture
def _patched_ansible_prepare(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("molecule.provisioner.ansible.Ansible.prepare")


# NOTE(retr0h): The use of the `patched_config_validate` fixture, disables
# config.Config._validate from executing.  Thus preventing odd side-effects
# throughout patched.assert_called unit tests.
def test_prepare_execute(  # noqa: D103
    mocker: MockerFixture,
    caplog: pytest.LogCaptureFixture,
    _patched_ansible_prepare: Mock,  # noqa: PT019
    patched_config_validate: Mock,
    config_instance: config.Config,
) -> None:
    pb = os.path.join(config_instance.scenario.directory, "prepare.yml")  # noqa: PTH118
    util.write_file(pb, "")

    p = prepare.Prepare(config_instance)
    p.execute()

    assert "default" in caplog.text
    assert "prepare" in caplog.text

    _patched_ansible_prepare.assert_called_once_with()

    assert config_instance.state.prepared


def test_execute_skips_when_instances_already_prepared(  # noqa: D103
    caplog: pytest.LogCaptureFixture,
    _patched_ansible_prepare: Mock,  # noqa: PT019
    config_instance: config.Config,
) -> None:
    config_instance.state.change_state("prepared", True)  # noqa: FBT003
    p = prepare.Prepare(config_instance)
    p.execute()

    msg = "Skipping, instances already prepared."
    assert msg in caplog.text

    assert not _patched_ansible_prepare.called


def test_prepare_execute_skips_when_playbook_not_configured(  # noqa: D103
    caplog: pytest.LogCaptureFixture,
    _patched_ansible_prepare: Mock,  # noqa: PT019
    config_instance: config.Config,
) -> None:
    p = prepare.Prepare(config_instance)
    p.execute()

    msg = "Skipping, prepare playbook not configured."
    assert msg in caplog.text

    assert not _patched_ansible_prepare.called


def test_execute_when_instances_already_prepared_but_force_provided(  # noqa: D103
    mocker: MockerFixture,
    caplog: pytest.LogCaptureFixture,
    _patched_ansible_prepare: Mock,  # noqa: PT019
    config_instance: config.Config,
) -> None:
    pb = os.path.join(config_instance.scenario.directory, "prepare.yml")  # noqa: PTH118
    util.write_file(pb, "")

    config_instance.state.change_state("prepared", True)  # noqa: FBT003
    config_instance.command_args = {"force": True}

    p = prepare.Prepare(config_instance)
    p.execute()

    _patched_ansible_prepare.assert_called_once_with()
