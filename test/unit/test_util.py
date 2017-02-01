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
import os

import colorama
import pytest
import sh

from molecule import config
from molecule import util

colorama.init(autoreset=True)


def test_print_debug(capsys):
    util.print_debug('test_title', 'test_data')
    result_title, _ = capsys.readouterr()

    print(''.join([
        colorama.Back.WHITE, colorama.Style.BRIGHT, colorama.Fore.BLACK,
        'DEBUG: ' + 'test_title', colorama.Fore.RESET, colorama.Back.RESET,
        colorama.Style.RESET_ALL
    ]))
    print(''.join([
        colorama.Fore.BLACK, colorama.Style.BRIGHT, 'test_data',
        colorama.Style.RESET_ALL, colorama.Fore.RESET
    ]))
    expected_title, _ = capsys.readouterr()

    assert expected_title == result_title


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


def test_run_command_with_debug(patched_print_debug):
    cmd = sh.ls.bake()
    util.run_command(cmd, debug=True)

    patched_print_debug.assert_called_once_with('COMMAND', sh.which('ls'))


def test_os_walk(temp_dir):
    scenarios = ['scenario1', 'scenario2', 'scenario3']
    molecule_directory = config.molecule_directory(temp_dir.strpath)
    for scenario in scenarios:
        scenario_directory = os.path.join(molecule_directory, scenario)
        molecule_file = config.molecule_file(scenario_directory)
        os.makedirs(scenario_directory)
        open(molecule_file, 'a').close()

    result = [f for f in util.os_walk(molecule_directory, 'molecule.yml')]
    assert 3 == len(result)


def test_render_template():
    template = "{{ foo }} = {{ bar}}"

    "foo = bar" == util.render_template(template, foo='foo', bar='bar')


def test_write_file(temp_dir):
    dest_file = os.path.join(temp_dir.strpath, 'test_util_write_file.tmp')
    contents = binascii.b2a_hex(os.urandom(15)).decode()
    util.write_file(dest_file, contents)
    with open(dest_file, 'r') as stream:
        data = stream.read()
    x = '# Molecule managed\n\n{}'.format(contents)

    assert x == data


def test_safe_dump():
    x = '---\nfoo: bar\n'

    assert x == util.safe_dump({'foo': 'bar'})


def test_safe_load():
    assert {'foo': 'bar'} == util.safe_load('foo: bar')


def test_safe_load_returns_empty_dict_on_empty_string():
    assert {} == util.safe_load('')


def test_safe_load_file(temp_dir):
    path = os.path.join(temp_dir.strpath, 'foo')
    util.write_file(path, 'foo: bar')

    assert {'foo': 'bar'} == util.safe_load_file(path)


def test_instance_with_scenario_name():
    assert 'foo-bar' == util.instance_with_scenario_name('foo', 'bar')


def test_ansi_escape():
    string = 'ls\r\n\x1b[00m\x1b[01;31mfoo\x1b[00m\r\n\x1b[01;31m'

    assert 'ls\r\nfoo\r\n' == util.ansi_escape(string)


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
