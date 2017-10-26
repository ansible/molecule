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

from __future__ import print_function

import binascii
import io
import os

import colorama
import pytest
import sh

from molecule import util

colorama.init(autoreset=True)


def test_print_debug(capsys):
    util.print_debug('test_title', 'test_data')
    result, _ = capsys.readouterr()
    title = [
        colorama.Back.WHITE, colorama.Style.BRIGHT, colorama.Fore.BLACK,
        'DEBUG: test_title', colorama.Fore.RESET, colorama.Back.RESET,
        colorama.Style.RESET_ALL
    ]
    print(''.join(title))

    data = [
        colorama.Fore.BLACK, colorama.Style.BRIGHT, 'test_data',
        colorama.Style.RESET_ALL, colorama.Fore.RESET
    ]
    print(''.join(data))

    x, _ = capsys.readouterr()
    assert x == result


def test_print_environment_vars(capsys):
    env = {
        'ANSIBLE_FOO': 'foo',
        'ANSIBLE_BAR': 'bar',
        'ANSIBLE': None,
        'MOLECULE_FOO': 'foo',
        'MOLECULE_BAR': 'bar',
        'MOLECULE': None
    }
    util.print_environment_vars(env)
    result, _ = capsys.readouterr()

    # Ansible Environment
    title = [
        colorama.Back.WHITE, colorama.Style.BRIGHT, colorama.Fore.BLACK,
        'DEBUG: ANSIBLE ENVIRONMENT', colorama.Fore.RESET, colorama.Back.RESET,
        colorama.Style.RESET_ALL
    ]
    print(''.join(title))
    data = [
        colorama.Fore.BLACK, colorama.Style.BRIGHT,
        util.safe_dump({
            'ANSIBLE_FOO': 'foo',
            'ANSIBLE_BAR': 'bar'
        }), colorama.Style.RESET_ALL, colorama.Fore.RESET
    ]
    print(''.join(data))

    # Molecule Environment
    title = [
        colorama.Back.WHITE, colorama.Style.BRIGHT, colorama.Fore.BLACK,
        'DEBUG: MOLECULE ENVIRONMENT', colorama.Fore.RESET,
        colorama.Back.RESET, colorama.Style.RESET_ALL
    ]
    print(''.join(title))
    data = [
        colorama.Fore.BLACK, colorama.Style.BRIGHT,
        util.safe_dump({
            'MOLECULE_FOO': 'foo',
            'MOLECULE_BAR': 'bar'
        }), colorama.Style.RESET_ALL, colorama.Fore.RESET
    ]
    print(''.join(data))

    # Shell Replay
    title = [
        colorama.Back.WHITE, colorama.Style.BRIGHT, colorama.Fore.BLACK,
        'DEBUG: SHELL REPLAY', colorama.Fore.RESET, colorama.Back.RESET,
        colorama.Style.RESET_ALL
    ]
    print(''.join(title))
    data = [
        colorama.Fore.BLACK, colorama.Style.BRIGHT,
        'ANSIBLE_BAR=bar ANSIBLE_FOO=foo MOLECULE_BAR=bar MOLECULE_FOO=foo',
        colorama.Style.RESET_ALL, colorama.Fore.RESET
    ]
    print(''.join(data))
    print()

    x, _ = capsys.readouterr()
    assert x == result


def test_sysexit():
    with pytest.raises(SystemExit) as e:
        util.sysexit()

    assert 1 == e.value.code


def test_sysexit_with_custom_code():
    with pytest.raises(SystemExit) as e:
        util.sysexit(2)

    assert 2 == e.value.code


def test_sysexit_with_message(patched_logger_critical):
    with pytest.raises(SystemExit) as e:
        util.sysexit_with_message('foo')

    assert 1 == e.value.code

    patched_logger_critical.assert_called_once_with('foo')


def test_sysexit_with_message_and_custom_code(patched_logger_critical):
    with pytest.raises(SystemExit) as e:
        util.sysexit_with_message('foo', 2)

    assert 2 == e.value.code

    patched_logger_critical.assert_called_once_with('foo')


def test_run_command():
    cmd = sh.ls.bake()
    x = util.run_command(cmd)

    assert 0 == x.exit_code


def test_run_command_with_debug(mocker, patched_print_debug):
    cmd = sh.ls.bake(_env={'ANSIBLE_FOO': 'foo', 'MOLECULE_BAR': 'bar'})
    util.run_command(cmd, debug=True)
    x = [
        mocker.call('ANSIBLE ENVIRONMENT', '---\nANSIBLE_FOO: foo\n'),
        mocker.call('MOLECULE ENVIRONMENT', '---\nMOLECULE_BAR: bar\n'),
        mocker.call('SHELL REPLAY', 'ANSIBLE_FOO=foo MOLECULE_BAR=bar'),
        mocker.call('COMMAND', sh.which('ls'))
    ]

    assert x == patched_print_debug.mock_calls


def test_run_command_with_debug_handles_no_env(mocker, patched_print_debug):
    cmd = sh.ls.bake()
    util.run_command(cmd, debug=True)
    x = [
        mocker.call('ANSIBLE ENVIRONMENT', '--- {}\n'),
        mocker.call('MOLECULE ENVIRONMENT', '--- {}\n'),
        mocker.call('SHELL REPLAY', ''),
        mocker.call('COMMAND', sh.which('ls'))
    ]

    assert x == patched_print_debug.mock_calls


def test_os_walk(temp_dir):
    scenarios = ['scenario1', 'scenario2', 'scenario3']
    molecule_directory = pytest.helpers.molecule_directory()
    for scenario in scenarios:
        scenario_directory = os.path.join(molecule_directory, scenario)
        molecule_file = pytest.helpers.get_molecule_file(scenario_directory)
        os.makedirs(scenario_directory)
        util.write_file(molecule_file, '')

    result = [f for f in util.os_walk(molecule_directory, 'molecule.yml')]
    assert 3 == len(result)


def test_render_template():
    template = "{{ foo }} = {{ bar }}"

    "foo = bar" == util.render_template(template, foo='foo', bar='bar')


def test_write_file(temp_dir):
    dest_file = os.path.join(temp_dir.strpath, 'test_util_write_file.tmp')
    contents = binascii.b2a_hex(os.urandom(15)).decode()
    util.write_file(dest_file, contents)
    with util.open_file(dest_file) as stream:
        data = stream.read()
    x = '# Molecule managed\n\n{}'.format(contents)

    assert x == data


def molecule_prepender(content):
    x = '# Molecule managed\n\nfoo bar'

    assert x == util.file_prepender('foo bar')


def test_safe_dump():
    x = """
---
foo: bar
""".lstrip()

    assert x == util.safe_dump({'foo': 'bar'})


def test_safe_dump_with_increase_indent():
    data = {
        'foo': [{
            'foo': 'bar',
            'baz': 'zzyzx',
        }],
    }

    x = """
---
foo:
  - baz: zzyzx
    foo: bar
""".lstrip()
    assert x == util.safe_dump(data)


def test_safe_load():
    assert {'foo': 'bar'} == util.safe_load('foo: bar')


def test_safe_load_returns_empty_dict_on_empty_string():
    assert {} == util.safe_load('')


def test_safe_load_file(temp_dir):
    path = os.path.join(temp_dir.strpath, 'foo')
    util.write_file(path, 'foo: bar')

    assert {'foo': 'bar'} == util.safe_load_file(path)


def test_open_file(temp_dir):
    path = os.path.join(temp_dir.strpath, 'foo')
    util.write_file(path, 'foo: bar')

    with util.open_file(path) as stream:
        try:
            file_types = (file, io.IOBase)
        except NameError:
            file_types = io.IOBase

        assert isinstance(stream, file_types)


def test_instance_with_scenario_name():
    assert 'foo-bar' == util.instance_with_scenario_name('foo', 'bar')


def test_strip_ansi_escape():
    string = 'ls\r\n\x1b[00m\x1b[01;31mfoo\x1b[00m\r\n\x1b[01;31m'

    assert 'ls\r\nfoo\r\n' == util.strip_ansi_escape(string)


def test_strip_ansi_color():
    s = 'foo\x1b[0m\x1b[0m\x1b[0m\n\x1b[0m\x1b[0m\x1b[0m\x1b[0m\x1b[0m'

    assert 'foo\n' == util.strip_ansi_color(s)


def test_verbose_flag():
    options = {'verbose': True, 'v': True}

    assert ['-v'] == util.verbose_flag(options)
    assert {} == options


def test_verbose_flag_extra_verbose():
    options = {'verbose': True, 'vvv': True}

    assert ['-vvv'] == util.verbose_flag(options)
    assert {} == options


def test_verbose_flag_preserves_verbose_option():
    options = {'verbose': True}

    assert [] == util.verbose_flag(options)
    assert {'verbose': True} == options


def test_title():
    assert 'Foo' == util.title('foo')
    assert 'Foo Bar' == util.title('foo_bar')


def test_exit_with_invalid_section(patched_logger_critical):
    with pytest.raises(SystemExit) as e:
        util.exit_with_invalid_section('section', 'name')

    assert 1 == e.value.code

    msg = "Invalid section named 'name' configured."
    patched_logger_critical.assert_called_once_with(msg)


def test_abs_path(temp_dir):
    x = os.path.abspath(
        os.path.join(os.getcwd(), os.path.pardir, 'foo', 'bar'))

    assert x == util.abs_path(os.path.join(os.path.pardir, 'foo', 'bar'))


def test_camelize():
    assert 'Foo' == util.camelize('foo')
    assert 'FooBar' == util.camelize('foo_bar')
    assert 'FooBarBaz' == util.camelize('foo_bar_baz')


def test_underscore():
    assert 'foo' == util.underscore('Foo')
    assert 'foo_bar' == util.underscore('FooBar')
    assert 'foo_bar_baz' == util.underscore('FooBarBaz')
