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

from molecule.provisioner import ansible_playbooks


@pytest.fixture
def _provisioner_section_data():
    return {
        'provisioner': {
            'name': 'ansible',
            'options': {},
            'lint': {
                'name': 'ansible-lint',
            },
            'config_options': {},
        },
    }


@pytest.fixture
def _instance(_provisioner_section_data, config_instance):
    return ansible_playbooks.AnsiblePlaybooks(config_instance)


def test_create_property(_instance):
    x = os.path.join(_instance._config.scenario.directory, 'create.yml')

    assert x == _instance._config.provisioner.playbooks.create


def test_converge_property(_instance):
    x = os.path.join(_instance._config.scenario.directory, 'playbook.yml')

    assert x == _instance._config.provisioner.playbooks.converge


def test_destroy_property(_instance):
    x = os.path.join(_instance._config.scenario.directory, 'destroy.yml')

    assert x == _instance._config.provisioner.playbooks.destroy


def test_prepare_property(_instance):
    x = os.path.join(_instance._config.scenario.directory, 'prepare.yml')

    assert x == _instance._config.provisioner.playbooks.prepare


def test_side_effect_property(_instance):
    assert _instance._config.provisioner.playbooks.side_effect is None


def test_verify_property(_instance):
    x = os.path.join(_instance._config.scenario.directory, 'verify.yml')

    assert x == _instance._config.provisioner.playbooks.verify


def test_get_ansible_playbook(_instance):
    x = os.path.join(_instance._config.scenario.directory, 'create.yml')

    assert x == _instance._get_ansible_playbook('create')


@pytest.fixture
def _provisioner_driver_section_data():
    return {
        'provisioner': {
            'name': 'ansible',
            'playbooks': {
                'docker': {
                    'create': 'docker-create.yml',
                },
                'create': 'create.yml',
            },
        }
    }


@pytest.mark.parametrize(
    'config_instance', ['_provisioner_driver_section_data'], indirect=True)
def test_get_ansible_playbook_with_driver_key(_instance):
    x = os.path.join(_instance._config.scenario.directory, 'docker-create.yml')
    assert x == _instance._get_ansible_playbook('create')


@pytest.fixture
def _provisioner_playbook_none_section_data():
    return {
        'provisioner': {
            'name': 'ansible',
            'playbooks': {
                'side_effect': None,
            },
        }
    }


@pytest.mark.parametrize(
    'config_instance', ['_provisioner_playbook_none_section_data'],
    indirect=True)
def test_get_ansible_playbook_when_playbook_none(_instance):
    assert _instance._get_ansible_playbook('side_effect') is None


@pytest.fixture
def _provisioner_driver_playbook_none_section_data():
    return {
        'provisioner': {
            'name': 'ansible',
            'playbooks': {
                'docker': {
                    'side_effect': None,
                },
                'side_effect': None,
            },
        }
    }


@pytest.mark.parametrize(
    'config_instance', ['_provisioner_driver_playbook_none_section_data'],
    indirect=True)
def test_get_ansible_playbook_with_driver_key_when_playbook_none(_instance):
    assert _instance._get_ansible_playbook('side_effect') is None


@pytest.fixture
def _provisioner_driver_playbook_key_missing_section_data():
    return {
        'provisioner': {
            'name': 'ansible',
            'playbooks': {
                'docker': {
                    'create': 'docker-create.yml',
                },
                'side_effect': 'side_effect.yml',
            },
        }
    }


@pytest.mark.parametrize(
    'config_instance',
    ['_provisioner_driver_playbook_key_missing_section_data'],
    indirect=True)
def test_get_ansible_playbook_with_driver_key_when_playbook_key_missing(
        _instance):
    x = os.path.join(_instance._config.scenario.directory, 'side_effect.yml')
    assert x == _instance._get_ansible_playbook('side_effect')
