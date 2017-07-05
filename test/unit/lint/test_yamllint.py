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

import pytest
import sh

from molecule import config
from molecule.lint import yamllint


@pytest.fixture
def molecule_lint_section_data():
    return {
        'lint': {
            'name': 'yamllint',
            'options': {
                'foo': 'bar',
            },
            'env': {
                'foo': 'bar',
            }
        }
    }


@pytest.fixture
def yamllint_instance(molecule_lint_section_data, config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_lint_section_data)

    return yamllint.Yamllint(config_instance)


def test_config_private_member(yamllint_instance):
    assert isinstance(yamllint_instance._config, config.Config)


def test_files_private_member(patched_get_files, yamllint_instance):
    x = [
        'foo.yml',
        'bar.yaml',
    ]

    assert x == yamllint_instance._files


def test_default_options_property(yamllint_instance):
    assert {} == yamllint_instance.default_options


def test_default_env_property(yamllint_instance):
    assert 'MOLECULE_FILE' in yamllint_instance.default_env
    assert 'MOLECULE_INVENTORY_FILE' in yamllint_instance.default_env
    assert 'MOLECULE_SCENARIO_DIRECTORY' in yamllint_instance.default_env
    assert 'MOLECULE_INSTANCE_CONFIG' in yamllint_instance.default_env


def test_name_property(yamllint_instance):
    assert 'yamllint' == yamllint_instance.name


def test_enabled_property(yamllint_instance):
    assert yamllint_instance.enabled


def test_options_property(yamllint_instance):
    x = {
        'foo': 'bar',
    }

    assert x == yamllint_instance.options


def test_options_property_handles_cli_args(yamllint_instance):
    yamllint_instance._config.args = {'debug': True}
    x = {
        'foo': 'bar',
    }

    # Does nothing.  The `yamllint` command does not support
    # a `debug` flag.
    assert x == yamllint_instance.options


def test_bake(patched_get_files, yamllint_instance):
    yamllint_instance.bake()
    x = '{} --foo=bar foo.yml bar.yaml'.format(str(sh.yamllint))

    assert x == yamllint_instance._yamllint_command


def test_execute(patched_get_files, patched_logger_info,
                 patched_logger_success, patched_run_command,
                 yamllint_instance):
    yamllint_instance._yamllint_command = 'patched-yamllint-command'
    yamllint_instance.execute()

    patched_run_command.assert_called_once_with(
        'patched-yamllint-command', debug=False)

    msg = 'Executing Yamllint on files found in {}/...'.format(
        yamllint_instance._config.project_directory)
    patched_logger_info.assert_called_once_with(msg)

    msg = 'Lint completed successfully.'
    patched_logger_success.assert_called_once_with(msg)


def test_execute_does_not_execute(patched_get_files, patched_logger_warn,
                                  patched_logger_success, patched_run_command,
                                  yamllint_instance):
    yamllint_instance._config.config['lint']['enabled'] = False
    yamllint_instance.execute()

    assert not patched_run_command.called

    msg = 'Skipping, lint is disabled.'
    patched_logger_warn.assert_called_once_with(msg)


def test_execute_bakes(patched_get_files, patched_run_command,
                       yamllint_instance):
    yamllint_instance.execute()

    assert yamllint_instance._yamllint_command is not None

    cmd = '{} --foo=bar foo.yml bar.yaml'.format(str(sh.yamllint))
    patched_run_command.assert_called_once_with(cmd, debug=False)


def test_executes_catches_and_exits_return_code(patched_run_command,
                                                yamllint_instance):
    patched_run_command.side_effect = sh.ErrorReturnCode_1(
        sh.yamllint, b'', b'')
    with pytest.raises(SystemExit) as e:
        yamllint_instance.execute()

    assert 1 == e.value.code
