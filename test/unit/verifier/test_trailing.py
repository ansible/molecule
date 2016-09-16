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

import pytest

from molecule.verifier import trailing


@pytest.fixture()
def trailing_instance(molecule_instance):
    return trailing.Trailing(molecule_instance)


def test_trailing_newline(trailing_instance):
    line = ['line1', 'line2', '']
    res = trailing_instance._trailing_newline(line)

    assert not res


def test_trailing_newline_matched(trailing_instance):
    line = ['line1', 'line2', '\n']
    res = trailing_instance._trailing_newline(line)

    assert res


def test_trailing_whitespace_success(trailing_instance):
    line = ['line1', 'line2', 'line3']
    res = trailing_instance._trailing_whitespace(line)

    assert [] == res


def test_trailing_whitespace_matched(trailing_instance):
    line = ['line1', 'line2', 'line3    ']
    res = trailing_instance._trailing_whitespace(line)

    assert res


def test_trailing_whitespace_matched_multiline(trailing_instance):
    line = ['line1', 'line2    ', 'line3', 'line4    ']
    res = trailing_instance._trailing_whitespace(line)

    assert [2, 4] == res
