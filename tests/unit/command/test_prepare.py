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
import os

from typing import TYPE_CHECKING

import pytest

from molecule import config, util
from molecule.command import prepare


if TYPE_CHECKING:
    from typing import Literal
    from unittest.mock import MagicMock, Mock

    from pytest_mock import MockerFixture

    from molecule.types import ProvisionerData


@pytest.fixture
def _command_provisioner_section_data() -> dict[
    Literal["provisioner"],
    ProvisionerData,
]:
    return {"provisioner": {"name": "ansible", "playbooks": {"prepare": "prepare.yml"}}}


@pytest.fixture
def _patched_ansible_prepare(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("molecule.provisioner.ansible.Ansible.prepare")


def test_prepare_execute(  # noqa: D103
    mocker: MockerFixture,
    caplog: pytest.LogCaptureFixture,
    _patched_ansible_prepare: Mock,  # noqa: PT019
    patched_config_validate: Mock,
    config_instance: config.Config,
) -> None:
    pb = os.path.join(config_instance.scenario.directory, "prepare.yml")  # noqa: PTH118
    util.write_file(pb, "")

    config_instance.action = "prepare"
    p = prepare.Prepare(config_instance)

    with caplog.at_level(logging.INFO):
        p.execute()

    expected_record_count = 2
    assert len(caplog.records) == expected_record_count
    expected_message = "INFO     [default > prepare] Completed: Successful"
    assert caplog.records[1].getMessage() == expected_message

    _patched_ansible_prepare.assert_called_once_with()


@pytest.mark.parametrize(
    "config_instance",
    ["_command_provisioner_section_data"],  # noqa: PT007
    indirect=True,
)
def test_prepare_execute_raises_when_provisioner_raises_an_exception(  # noqa: D103
    _patched_ansible_prepare: Mock,  # noqa: PT019
    patched_config_validate: Mock,
    config_instance: config.Config,
) -> None:
    _patched_ansible_prepare.side_effect = Exception("foo")

    pb = os.path.join(config_instance.scenario.directory, "prepare.yml")  # noqa: PTH118
    util.write_file(pb, "")

    p = prepare.Prepare(config_instance)

    with pytest.raises(Exception) as cm:  # noqa: PT011
        p.execute()

    assert "foo" in str(cm.value)


def test_prepare_execute_skips_when_playbook_not_configured(  # noqa: D103
    caplog: pytest.LogCaptureFixture,
    _patched_ansible_prepare: Mock,  # noqa: PT019
    config_instance: config.Config,
) -> None:
    with caplog.at_level(logging.INFO):
        p = prepare.Prepare(config_instance)
        p.execute()

    completion_records = [r for r in caplog.records if "Completed:" in r.getMessage()]
    assert len(completion_records) >= 1, "Should have completion message"

    record = completion_records[0]
    assert "Missing playbook" in record.getMessage()
    assert hasattr(record, "molecule_scenario")
    assert record.molecule_scenario == "default"

    assert not _patched_ansible_prepare.called
