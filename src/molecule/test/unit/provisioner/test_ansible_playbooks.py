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
from molecule.provisioner import ansible_playbooks
from molecule.test.unit.conftest import os_split


@pytest.fixture
def _provisioner_section_data():
    return {"provisioner": {"name": "ansible", "options": {}, "config_options": {}}}


@pytest.fixture
def _instance(_provisioner_section_data, config_instance):
    return ansible_playbooks.AnsiblePlaybooks(config_instance)


def test_cleanup_property_is_optional(_instance):
    assert _instance._config.provisioner.playbooks.cleanup is None


@pytest.mark.skip(reason="create not running for delegated")
def test_create_property(_instance):
    x = os.path.join(_instance._get_playbook_directory(), "delegated", "create.yml")

    assert x == _instance._config.provisioner.playbooks.create


def test_converge_property(_instance):
    x = os.path.join(_instance._config.scenario.directory, "converge.yml")

    assert x == _instance._config.provisioner.playbooks.converge


@pytest.mark.skip(reason="destroy not running for delegated")
def test_destroy_property(_instance):
    x = os.path.join(_instance._get_playbook_directory(), "delegated", "destroy.yml")

    assert x == _instance._config.provisioner.playbooks.destroy


def test_prepare_property(_instance):
    assert _instance._config.provisioner.playbooks.prepare is None


def test_side_effect_property(_instance):
    assert _instance._config.provisioner.playbooks.side_effect is None


def test_verify_property(_instance):
    assert _instance._config.provisioner.playbooks.verify is None


def test_get_playbook_directory(_instance):
    result = _instance._get_playbook_directory()
    parts = os_split(result)
    x = ("molecule", "provisioner", "ansible", "playbooks")

    assert x == parts[-4:]


def test_get_playbook(tmpdir, _instance):
    x = os.path.join(_instance._config.scenario.directory, "create.yml")
    util.write_file(x, "")

    assert x == _instance._get_playbook("create")


@pytest.mark.skip(reason="create not running for delegated")
def test_get_playbook_returns_bundled_driver_playbook_when_local_not_found(
    tmpdir, _instance
):
    x = os.path.join(_instance._get_playbook_directory(), "delegated", "create.yml")

    assert x == _instance._get_playbook("create")


@pytest.fixture
def _provisioner_driver_section_data():
    return {
        "provisioner": {
            "name": "ansible",
            "playbooks": {
                "create": "create.yml",
            },
        }
    }


@pytest.fixture
def _provisioner_driver_playbook_key_missing_section_data():
    return {
        "provisioner": {
            "name": "ansible",
            "playbooks": {
                "side_effect": "side_effect.yml",
            },
        }
    }


@pytest.mark.parametrize(
    "config_instance",
    ["_provisioner_driver_playbook_key_missing_section_data"],
    indirect=True,
)
def test_get_ansible_playbook_with_driver_key_when_playbook_key_missing(
    tmpdir, _instance
):
    x = os.path.join(_instance._config.scenario.directory, "side_effect.yml")
    util.write_file(x, "")

    assert x == _instance._get_playbook("side_effect")


def test_get_bundled_driver_playbook(_instance):
    result = _instance._get_bundled_driver_playbook("create")
    parts = os_split(result)
    x = ("molecule", "driver", "playbooks", "create.yml")

    assert x == parts[-4:]
