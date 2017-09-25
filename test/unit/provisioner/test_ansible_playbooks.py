#  Copyright (c) 2015-2017 Cisco Systems, Inc.
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
def playbooks_instance(molecule_provisioner_section_data, config_instance):
    return ansible_playbooks.AnsiblePlaybooks(config_instance)


def test_create_property(playbooks_instance):
    x = os.path.join(playbooks_instance._config.scenario.directory,
                     'create.yml')

    assert x == playbooks_instance._config.provisioner.playbooks.create


def test_converge_property(playbooks_instance):
    x = os.path.join(playbooks_instance._config.scenario.directory,
                     'playbook.yml')

    assert x == playbooks_instance._config.provisioner.playbooks.converge


def test_destroy_property(playbooks_instance):
    x = os.path.join(playbooks_instance._config.scenario.directory,
                     'destroy.yml')

    assert x == playbooks_instance._config.provisioner.playbooks.destroy


def test_prepare_property(playbooks_instance):
    x = os.path.join(playbooks_instance._config.scenario.directory,
                     'prepare.yml')

    assert x == playbooks_instance._config.provisioner.playbooks.prepare


def test_side_effect_property(playbooks_instance):
    assert playbooks_instance._config.provisioner.playbooks.side_effect is None


def test_get_ansible_playbook(playbooks_instance):
    x = os.path.join(playbooks_instance._config.scenario.directory,
                     'create.yml')

    assert x == playbooks_instance._get_ansible_playbook('create')


@pytest.fixture
def molecule_provisioner_driver_section_data():
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


def test_get_ansible_playbook_with_driver_key(
        molecule_provisioner_driver_section_data, playbooks_instance):
    playbooks_instance._config.merge_dicts(
        playbooks_instance._config.config,
        molecule_provisioner_driver_section_data)

    x = os.path.join(playbooks_instance._config.scenario.directory,
                     'docker-create.yml')
    assert x == playbooks_instance._get_ansible_playbook('create')


@pytest.fixture
def molecule_provisioner_playbook_none_section_data():
    return {
        'provisioner': {
            'name': 'ansible',
            'playbooks': {
                'side_effect': None,
            },
        }
    }


def test_get_ansible_playbook_when_playbook_none(
        molecule_provisioner_playbook_none_section_data, playbooks_instance):
    playbooks_instance._config.merge_dicts(
        playbooks_instance._config.config,
        molecule_provisioner_playbook_none_section_data)

    assert playbooks_instance._get_ansible_playbook('side_effect') is None


@pytest.fixture
def molecule_provisioner_driver_playbook_none_section_data():
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


def test_get_ansible_playbook_with_driver_key_when_playbook_none(
        molecule_provisioner_driver_playbook_none_section_data,
        playbooks_instance):
    playbooks_instance._config.merge_dicts(
        playbooks_instance._config.config,
        molecule_provisioner_driver_playbook_none_section_data)

    assert playbooks_instance._get_ansible_playbook('side_effect') is None


@pytest.fixture
def molecule_provisioner_driver_playbook_key_missing_section_data():
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


def test_get_ansible_playbook_with_driver_key_when_playbook_key_missing(
        molecule_provisioner_driver_playbook_key_missing_section_data,
        playbooks_instance):
    playbooks_instance._config.merge_dicts(
        playbooks_instance._config.config,
        molecule_provisioner_driver_playbook_key_missing_section_data)

    x = os.path.join(playbooks_instance._config.scenario.directory,
                     'side_effect.yml')
    assert x == playbooks_instance._get_ansible_playbook('side_effect')
