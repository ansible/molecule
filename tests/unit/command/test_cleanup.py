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
from molecule.command import cleanup


if TYPE_CHECKING:
    from typing import Literal
    from unittest.mock import MagicMock, Mock

    from pytest_mock import MockerFixture

    from molecule.types import ProvisionerData


@pytest.fixture
def _command_provisioner_section_with_cleanup_data() -> (
    dict[Literal["provisioner"], ProvisionerData]
):
    return {"provisioner": {"name": "ansible", "playbooks": {"cleanup": "cleanup.yml"}}}


@pytest.fixture
def _patched_ansible_cleanup(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("molecule.provisioner.ansible.Ansible.cleanup")


# NOTE(retr0h): The use of the `patched_config_validate` fixture, disables
# config.Config._validate from executing.  Thus preventing odd side-effects
# throughout patched.assert_called unit tests.
@pytest.mark.parametrize(
    "config_instance",
    ["_command_provisioner_section_with_cleanup_data"],  # noqa: PT007
    indirect=True,
)
def test_cleanup_execute(  # noqa: D103
    mocker: MockerFixture,  # noqa: ARG001
    _patched_ansible_cleanup: Mock,  # noqa: PT019
    caplog: pytest.LogCaptureFixture,
    patched_config_validate: Mock,  # noqa: ARG001
    config_instance: config.Config,
) -> None:
    pb = os.path.join(config_instance.scenario.directory, "cleanup.yml")  # noqa: PTH118
    util.write_file(pb, "")

    cu = cleanup.Cleanup(config_instance)
    cu.execute()

    assert "cleanup" in caplog.text

    _patched_ansible_cleanup.assert_called_once_with()


def test_cleanup_execute_skips_when_playbook_not_configured(  # noqa: D103
    caplog: pytest.LogCaptureFixture,
    _patched_ansible_cleanup: Mock,  # noqa: PT019
    config_instance: config.Config,
) -> None:
    cu = cleanup.Cleanup(config_instance)
    cu.execute()

    msg = "Skipping, cleanup playbook not configured."
    assert msg in caplog.text

    assert not _patched_ansible_cleanup.called
