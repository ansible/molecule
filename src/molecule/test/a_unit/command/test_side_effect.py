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

import os

import pytest
from pytest_mock import MockerFixture

from molecule import config, util
from molecule.command import side_effect


@pytest.fixture()
def _command_provisioner_section_with_side_effect_data():
    return {
        "provisioner": {
            "name": "ansible",
            "playbooks": {"side_effect": "side_effect.yml"},
        },
    }


@pytest.fixture()
def _patched_ansible_side_effect(mocker):
    return mocker.patch("molecule.provisioner.ansible.Ansible.side_effect")


# NOTE(retr0h): The use of the `patched_config_validate` fixture, disables
# config.Config._validate from executing.  Thus preventing odd side-effects
# throughout patched.assert_called unit tests.
@pytest.mark.parametrize(
    "config_instance",
    ["_command_provisioner_section_with_side_effect_data"],
    indirect=True,
)
def test_execute(
    mocker: MockerFixture,
    _patched_ansible_side_effect,
    caplog,
    patched_config_validate,
    config_instance: config.Config,
):
    pb = os.path.join(config_instance.scenario.directory, "side_effect.yml")
    util.write_file(pb, "")

    se = side_effect.SideEffect(config_instance)
    se.execute()

    assert "default" in caplog.text
    assert "side_effect" in caplog.text

    _patched_ansible_side_effect.assert_called_once_with(None)


def test_execute_skips_when_playbook_not_configured(
    caplog,
    _patched_ansible_side_effect,
    config_instance: config.Config,
):
    se = side_effect.SideEffect(config_instance)
    se.execute()

    msg = "Skipping, side effect playbook not configured."
    assert msg in caplog.text

    assert not _patched_ansible_side_effect.called
