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
from molecule import util
from molecule.lint import trailing


@pytest.fixture
def molecule_lint_section_data():
    return {
        'lint': {
            'name': 'ansible-lint',
            'options': {
                'foo': 'bar',
            },
            'env': {
                'foo': 'bar',
            },
            'trailing_ignore_paths': [
                '.foo',
                '.bar',
            ],
        }
    }


@pytest.fixture
def trailing_instance(molecule_lint_section_data, config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_lint_section_data)

    return trailing.Trailing(config_instance)


def test_config_private_member(trailing_instance):
    assert isinstance(trailing_instance._config, config.Config)


def test_default_options_property(trailing_instance):
    assert {} == trailing_instance.default_options


def test_options_property(trailing_instance):
    assert {'foo': 'bar', } == trailing_instance.options


def test_default_env_property(trailing_instance):
    assert 'MOLECULE_FILE' in trailing_instance.default_env
    assert 'MOLECULE_INVENTORY_FILE' in trailing_instance.default_env
    assert 'MOLECULE_SCENARIO_DIRECTORY' in trailing_instance.default_env
    assert 'MOLECULE_INSTANCE_CONFIG' in trailing_instance.default_env


def test_env_property(trailing_instance):
    assert 'bar' == trailing_instance.env['foo']


def test_default_ignore_paths_property(trailing_instance):
    assert [] == trailing_instance.default_ignore_paths


def test_ignore_paths_property(trailing_instance):
    x = [
        '.foo',
        '.bar',
    ]

    x == trailing_instance.ignore_paths


def test_execute_has_trailing_newline(trailing_instance,
                                      patched_logger_critical):
    project_directory = trailing_instance._config.project_directory
    f = os.path.join(project_directory, 'foo.yml')
    util.write_file(f, 'foo\n\n')

    trailing_instance._tests = trailing_instance._get_tests()

    with pytest.raises(SystemExit) as e:
        trailing_instance.execute()

    assert 1 == e.value.code

    msg = 'Trailing newline found at the end of {}.'.format(f)
    patched_logger_critical.assert_called_once_with(msg)


def test_execute_has_trailing_whitespace(trailing_instance,
                                         patched_logger_critical):
    project_directory = trailing_instance._config.project_directory
    f = os.path.join(project_directory, 'foo.yml')
    util.write_file(f, 'foo  ')

    trailing_instance._tests = trailing_instance._get_tests()

    with pytest.raises(SystemExit) as e:
        trailing_instance.execute()

    assert 1 == e.value.code

    msg = 'Trailing whitespace found in {} on lines: {}'.format(f, 3)
    patched_logger_critical.assert_called_once_with(msg)


def test_get_trailing_newline(trailing_instance):
    line = ['line1', 'line2', '']
    res = trailing_instance._get_trailing_newline(line)

    assert not res


def test_get_trailing_newline_matched(trailing_instance):
    line = ['line1', 'line2', '\n']
    res = trailing_instance._get_trailing_newline(line)

    assert res


def test_get_trailing_whitespace(trailing_instance):
    line = ['line1', 'line2', 'line3']
    res = trailing_instance._get_trailing_whitespace(line)

    assert [] == res


def test_get_trailing_whitespace_matched(trailing_instance):
    line = ['line1', 'line2', 'line3    ']
    res = trailing_instance._get_trailing_whitespace(line)

    assert res


def test_get_trailing_whitespace_matched_multiline(trailing_instance):
    line = ['line1', 'line2    ', 'line3', 'line4    ']
    res = trailing_instance._get_trailing_whitespace(line)

    assert [2, 4] == res


def test_get_tests(trailing_instance):
    project_directory = trailing_instance._config.project_directory

    for d in [
            '.foo',
            '.bar',
    ]:
        os.mkdir(os.path.join(project_directory, d))

    for f in [
            'foo.yml',
            'foo.yaml',
            'foo.py',
            '.foo/foo.yml',
            '.bar/foo.yml',
    ]:
        util.write_file(os.path.join(project_directory, f), '')

    # NOTE(retr0h): Unit tests add a molecule.yml automatically.
    assert 4 == len(trailing_instance._get_tests())
