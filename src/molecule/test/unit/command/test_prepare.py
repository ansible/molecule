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

from molecule import util
from molecule.command import prepare


@pytest.fixture
def _patched_ansible_prepare(mocker):
    return mocker.patch("molecule.provisioner.ansible.Ansible.prepare")


# NOTE(retr0h): The use of the `patched_config_validate` fixture, disables
# config.Config._validate from executing.  Thus preventing odd side-effects
# throughout patched.assert_called unit tests.
def test_execute(
    mocker,
    patched_logger_info,
    _patched_ansible_prepare,
    patched_config_validate,
    config_instance,
):
    pb = os.path.join(config_instance.scenario.directory, "prepare.yml")
    util.write_file(pb, "")

    p = prepare.Prepare(config_instance)
    p.execute()

    assert len(patched_logger_info.mock_calls) == 1
    name, args, kwargs = patched_logger_info.mock_calls[0]
    assert "default" in args
    assert "prepare" in args

    _patched_ansible_prepare.assert_called_once_with()

    assert config_instance.state.prepared


def test_execute_skips_when_instances_already_prepared(
    patched_logger_warning, _patched_ansible_prepare, config_instance
):
    config_instance.state.change_state("prepared", True)
    p = prepare.Prepare(config_instance)
    p.execute()

    msg = "Skipping, instances already prepared."
    patched_logger_warning.assert_called_once_with(msg)

    assert not _patched_ansible_prepare.called


def test_execute_skips_when_playbook_not_configured(
    patched_logger_warning, _patched_ansible_prepare, config_instance
):

    p = prepare.Prepare(config_instance)
    p.execute()

    msg = "Skipping, prepare playbook not configured."
    patched_logger_warning.assert_called_once_with(msg)

    assert not _patched_ansible_prepare.called


def test_execute_when_instances_already_prepared_but_force_provided(
    mocker, patched_logger_warning, _patched_ansible_prepare, config_instance
):
    pb = os.path.join(config_instance.scenario.directory, "prepare.yml")
    util.write_file(pb, "")

    config_instance.state.change_state("prepared", True)
    config_instance.command_args = {"force": True}

    p = prepare.Prepare(config_instance)
    p.execute()

    _patched_ansible_prepare.assert_called_once_with()
