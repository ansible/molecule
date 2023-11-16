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


import pytest
from pytest_mock import MockerFixture

from molecule import config
from molecule.command import create


@pytest.fixture()
def _patched_create_setup(mocker):
    return mocker.patch("molecule.command.create.Create._setup")


# NOTE(retr0h): The use of the `patched_config_validate` fixture, disables
# config.Config._validate from executing.  Thus preventing odd side-effects
# throughout patched.assert_called unit tests.
@pytest.mark.skip(reason="create not running for delegated")
def test_create_execute(
    mocker: MockerFixture,
    caplog,
    command_patched_ansible_create,
    patched_config_validate,
    config_instance: config.Config,
):
    c = create.Create(config_instance)
    c.execute()

    assert "default" in caplog.text
    assert "converge" in caplog.text

    assert config_instance.state.driver == "default"

    command_patched_ansible_create.assert_called_once_with()

    assert config_instance.state.created


@pytest.mark.skip(reason="create not running for delegated")
def test_execute_skips_when_instances_already_created(
    caplog,
    command_patched_ansible_create,
    config_instance: config.Config,
):
    config_instance.state.change_state("created", True)
    c = create.Create(config_instance)
    c.execute()

    msg = "Skipping, instances already created."
    assert msg in caplog.text

    assert not command_patched_ansible_create.called
