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

from molecule import config
from molecule.verifier import goss


@pytest.fixture
def molecule_verifier_section_data():
    return {
        'verifier': {
            'name': 'goss',
            'options': {
                'foo': 'bar',
                'retry-timeout': '30s',
            },
            'env': {
                'foo': 'bar',
            },
            'lint': {
                'name': 'None',
            },
        }
    }


@pytest.fixture
def goss_instance(molecule_verifier_section_data, config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_verifier_section_data)

    return goss.Goss(config_instance)


def test_config_private_member(goss_instance):
    assert isinstance(goss_instance._config, config.Config)


def test_default_options_property(goss_instance):
    assert {} == goss_instance.default_options


def test_default_env_property(goss_instance):
    assert 'MOLECULE_FILE' in goss_instance.default_env
    assert 'MOLECULE_INVENTORY_FILE' in goss_instance.default_env
    assert 'MOLECULE_SCENARIO_DIRECTORY' in goss_instance.default_env
    assert 'MOLECULE_INSTANCE_CONFIG' in goss_instance.default_env


def test_env_property(goss_instance):
    assert 'bar' == goss_instance.env['foo']


def test_lint_property(goss_instance):
    assert goss_instance.lint is None


@pytest.fixture
def molecule_verifier_lint_invalid_section_data():
    return {
        'verifier': {
            'name': 'goss',
            'lint': {
                'name': 'invalid',
            },
        }
    }


def test_lint_property_raises(molecule_verifier_lint_invalid_section_data,
                              patched_logger_critical, goss_instance):
    goss_instance._config.merge_dicts(
        goss_instance._config.config,
        molecule_verifier_lint_invalid_section_data)
    with pytest.raises(SystemExit) as e:
        goss_instance.lint

    assert 1 == e.value.code

    msg = "Invalid lint named 'invalid' configured."
    patched_logger_critical.assert_called_once_with(msg)


def test_name_property(goss_instance):
    assert 'goss' == goss_instance.name


def test_enabled_property(goss_instance):
    assert goss_instance.enabled


def test_directory_property(goss_instance):
    parts = goss_instance.directory.split(os.path.sep)

    assert 'tests' == parts[-1]


def test_options_property(goss_instance):
    x = {
        'foo': 'bar',
        'retry-timeout': '30s',
    }

    assert x == goss_instance.options


def test_options_property_handles_cli_args(goss_instance):
    goss_instance._config.args = {'debug': True}
    x = {
        'foo': 'bar',
        'retry-timeout': '30s',
    }

    # Does nothing.  The `goss` command does not support
    # a `debug` flag.
    assert x == goss_instance.options


def test_bake(goss_instance):
    assert goss_instance.bake() is None


def test_execute(patched_logger_info, patched_ansible_converge,
                 patched_goss_get_tests, patched_logger_success,
                 goss_instance):
    goss_instance.execute()

    goss_playbook = os.path.join(goss_instance._config.scenario.directory,
                                 'verifier.yml')
    patched_ansible_converge.assert_called_once_with(goss_playbook)

    msg = 'Executing Goss tests found in {}/...'.format(
        goss_instance.directory)
    patched_logger_info.assert_called_once_with(msg)

    msg = 'Verifier completed successfully.'
    patched_logger_success.assert_called_once_with(msg)


def test_execute_does_not_execute(patched_ansible_converge,
                                  patched_logger_warn, goss_instance):
    goss_instance._config.config['verifier']['enabled'] = False
    goss_instance.execute()

    assert not patched_ansible_converge.called

    msg = 'Skipping, verifier is disabled.'
    patched_logger_warn.assert_called_once_with(msg)


def test_does_not_execute_without_tests(patched_ansible_converge,
                                        patched_logger_warn, goss_instance):
    goss_instance.execute()

    assert not patched_ansible_converge.called

    msg = 'Skipping, no tests found.'
    patched_logger_warn.assert_called_once_with(msg)


def test_execute_bakes():
    pass
