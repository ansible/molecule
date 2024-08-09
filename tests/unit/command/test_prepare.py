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

import pytest

from pytest_mock import MockerFixture

from molecule import config, util
from molecule.command import prepare


@pytest.fixture()
def _patched_ansible_prepare(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN202, PT005
    return mocker.patch("molecule.provisioner.ansible.Ansible.prepare")


# NOTE(retr0h): The use of the `patched_config_validate` fixture, disables
# config.Config._validate from executing.  Thus preventing odd side-effects
# throughout patched.assert_called unit tests.
def test_prepare_execute(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    mocker: MockerFixture,  # noqa: ARG001
    caplog,  # noqa: ANN001
    _patched_ansible_prepare,  # noqa: ANN001, PT019
    patched_config_validate,  # noqa: ANN001, ARG001
    config_instance: config.Config,
):
    pb = os.path.join(config_instance.scenario.directory, "prepare.yml")  # noqa: PTH118
    util.write_file(pb, "")

    p = prepare.Prepare(config_instance)
    p.execute()  # type: ignore[no-untyped-call]

    assert "default" in caplog.text
    assert "prepare" in caplog.text

    _patched_ansible_prepare.assert_called_once_with()

    assert config_instance.state.prepared


def test_execute_skips_when_instances_already_prepared(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    caplog,  # noqa: ANN001
    _patched_ansible_prepare,  # noqa: ANN001, PT019
    config_instance: config.Config,
):
    config_instance.state.change_state("prepared", True)  # noqa: FBT003
    p = prepare.Prepare(config_instance)
    p.execute()  # type: ignore[no-untyped-call]

    msg = "Skipping, instances already prepared."
    assert msg in caplog.text

    assert not _patched_ansible_prepare.called


def test_prepare_execute_skips_when_playbook_not_configured(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    caplog,  # noqa: ANN001
    _patched_ansible_prepare,  # noqa: ANN001, PT019
    config_instance: config.Config,
):
    p = prepare.Prepare(config_instance)
    p.execute()  # type: ignore[no-untyped-call]

    msg = "Skipping, prepare playbook not configured."
    assert msg in caplog.text

    assert not _patched_ansible_prepare.called


def test_execute_when_instances_already_prepared_but_force_provided(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    mocker: MockerFixture,  # noqa: ARG001
    caplog,  # noqa: ANN001, ARG001
    _patched_ansible_prepare,  # noqa: ANN001, PT019
    config_instance: config.Config,
):
    pb = os.path.join(config_instance.scenario.directory, "prepare.yml")  # noqa: PTH118
    util.write_file(pb, "")

    config_instance.state.change_state("prepared", True)  # noqa: FBT003
    config_instance.command_args = {"force": True}

    p = prepare.Prepare(config_instance)
    p.execute()  # type: ignore[no-untyped-call]

    _patched_ansible_prepare.assert_called_once_with()
