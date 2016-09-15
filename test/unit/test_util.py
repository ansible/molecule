#  Copyright (c) 2015-2016 Cisco Systems, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

import binascii
import os

import colorama
import pytest

from molecule import util


def test_print_success(capsys):
    util.print_success('test')
    result, _ = capsys.readouterr()

    print '{}{}'.format(colorama.Fore.GREEN, 'test'.rstrip())
    expected, _ = capsys.readouterr()

    assert expected == result


def test_print_info(capsys):
    util.print_info('test')
    result, _ = capsys.readouterr()

    print '--> {}{}'.format(colorama.Fore.CYAN, 'test'.rstrip())
    expected, _ = capsys.readouterr()

    assert expected == result


# TODO(retr0h): Cleanup how we deal with temp files
def test_write_template():
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'support')
    src = os.path.join(d, 'test_write_template.j2')
    tmp_file = '/tmp/test_util_write_template.tmp'
    util.write_template(src, tmp_file, {'test': 'chicken'})
    with open(tmp_file, 'r') as f:
        data = f.read()
    os.remove(tmp_file)

    assert data == 'this is a chicken\n'


# TODO(retr0h): Cleanup how we deal with temp files
def test_write_file():
    tmp_file = '/tmp/test_util_write_file.tmp'
    contents = binascii.b2a_hex(os.urandom(15))
    util.write_file(tmp_file, contents)
    with open(tmp_file, 'r') as f:
        data = f.read()
    os.remove(tmp_file)

    assert data == contents


def test_format_instance_name_00():
    instances = [{'name': 'test-01'}]
    actual = util.format_instance_name('test-02', 'rhel-7', instances)

    assert actual is None


def test_format_instance_name_01():
    instances = [{'name': 'test-01'}]
    actual = util.format_instance_name('test-01', 'rhel-7', instances)

    assert 'test-01' == actual


def test_format_instance_name_02():
    instances = [{'name': 'test-01',
                  'options': {'append_platform_to_hostname': True}}]
    actual = util.format_instance_name('test-01', 'rhel-7', instances)

    assert 'test-01-rhel-7' == actual


def test_format_instance_name_03():
    instances = [{'name': 'test-01', 'options': {'chicken': False}}]
    actual = util.format_instance_name('test-01', 'rhel-7', instances)

    assert 'test-01' == actual


@pytest.mark.skipif(reason="determine how to test such a function")
def test_check_ssh_availability():
    pass


def test_debug(capsys):
    util.print_debug('test_title', 'test_data')
    result_title, _ = capsys.readouterr()

    print(''.join(
        [colorama.Back.WHITE, colorama.Style.BRIGHT, colorama.Fore.BLACK,
         'DEBUG: ' + 'test_title', colorama.Fore.RESET, colorama.Back.RESET,
         colorama.Style.RESET_ALL]))
    print(''.join([colorama.Fore.BLACK, colorama.Style.BRIGHT, 'test_data',
                   colorama.Style.RESET_ALL, colorama.Fore.RESET]))
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


def test_get_cookiecutter_template_dir():
    result = util._get_cookiecutter_template_dir('foo')
    parts = pytest.helpers.os_split(result)

    assert ('molecule', 'cookiecutter', 'foo') == parts[-3:]
