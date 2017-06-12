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

import colorama
import pytest

from molecule import logger


def test_info(capsys):
    log = logger.get_logger(__name__)
    log.info('foo')
    stdout, _ = capsys.readouterr()

    print('--> {}{}'.format(colorama.Fore.CYAN, 'foo'.rstrip()))
    x, _ = capsys.readouterr()

    assert x == stdout


def test_out(capsys):
    log = logger.get_logger(__name__)
    log.out('foo')

    stdout, _ = capsys.readouterr()

    assert '    foo\n' == stdout


def test_warn(capsys):
    log = logger.get_logger(__name__)
    log.warn('foo')

    stdout, _ = capsys.readouterr()

    print('{}{}'.format(colorama.Fore.YELLOW, 'foo'.rstrip()))
    x, _ = capsys.readouterr()

    assert x == stdout


@pytest.mark.skip(reason='TODO(retr0h): understand how to test this')
def test_error(capsys):
    log = logger.get_logger(__name__)
    log.error('foo')

    _, stderr = capsys.readouterr()

    print('{}{}'.format(colorama.fore.red, 'foo'.rstrip()))
    _, x = capsys.readouterr()

    assert x == stderr


@pytest.mark.skip(reason='TODO(retr0h): understand how to test this')
def test_critical(capsys):
    log = logger.get_logger(__name__)
    log.critical('foo')

    _, stderr = capsys.readouterr()

    print('{}error: {}'.format(colorama.fore.red, 'foo'.rstrip()))
    _, x = capsys.readouterr()

    assert x == stderr


def test_success(capsys):
    log = logger.get_logger(__name__)
    log.success('foo')

    stdout, _ = capsys.readouterr()

    print('{}{}'.format(colorama.Fore.GREEN, 'foo'.rstrip()))
    x, _ = capsys.readouterr()

    assert x == stdout
