#  Copyright (c) 2015-2016 Cisco Systems, Inc.
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

import colorama
import os
import pytest
import sh

from molecule import config
from molecule import util

colorama.init(autoreset=True)


def test_print_success(capsys):
    util.print_success('test')
    result, _ = capsys.readouterr()

    print('{}{}'.format(colorama.Fore.GREEN, 'test'.rstrip()))
    x, _ = capsys.readouterr()

    assert x == result


def test_print_info(capsys):
    util.print_info('test')
    result, _ = capsys.readouterr()

    print('--> {}{}'.format(colorama.Fore.CYAN, 'test'.rstrip()))
    x, _ = capsys.readouterr()

    assert x == result


def test_print_info_without_pretty(capsys):
    util.print_info('test', pretty=False)
    result, _ = capsys.readouterr()

    print('{}'.format('test'.rstrip()))
    x, _ = capsys.readouterr()

    assert x == result


def test_print_warn(capsys):
    util.print_warn('test')
    result, _ = capsys.readouterr()

    print('{}{}'.format(colorama.Fore.YELLOW, 'test'.rstrip()))
    x, _ = capsys.readouterr()

    assert x == result


def test_print_error(capsys):
    util.print_error('test')
    _, result = capsys.readouterr()

    print('{}ERROR: {}'.format(colorama.Fore.RED, 'test'.rstrip()))
    x, _ = capsys.readouterr()

    assert x == result


def test_print_error_without_pretty(capsys):
    util.print_error('test', pretty=False)
    x, result = capsys.readouterr()

    print('{}{}'.format(colorama.Fore.RED, 'test'.rstrip()))
    x, _ = capsys.readouterr()

    assert x == result


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


def test_callback_info(patched_print_info):
    util.callback_info('test')

    patched_print_info.assert_called_with('test', pretty=False)


def test_callback_error(patched_print_error):
    util.callback_error('test')

    patched_print_error.assert_called_with('test', pretty=False)


def test_sysexit():
    with pytest.raises(SystemExit) as e:
        util.sysexit()

    assert 1 == e.value.code


def test_sysexit_with_custom_code():
    with pytest.raises(SystemExit) as e:
        util.sysexit(2)

    assert 2 == e.value.code


def test_run_command():
    cmd = sh.ls.bake()
    x = util.run_command(cmd)

    assert 0 == x.exit_code


def test_run_command_with_debug(patched_print_debug):
    cmd = sh.ls.bake()
    util.run_command(cmd, debug=True)

    patched_print_debug.assert_called_with('COMMAND', sh.which('ls'))


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
