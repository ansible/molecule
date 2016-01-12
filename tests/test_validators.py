#  Copyright (c) 2015 Cisco Systems
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

import testtools
from mock import patch

import molecule.validators as validators


class TestValidators(testtools.TestCase):
    def test_trailing_newline_failed(self):
        line = ['line1', 'line2', '\n']
        res = validators.trailing_newline(line)

        self.assertTrue(res)

    def test_trailing_newline_success(self):
        line = ['line1', 'line2', '']
        res = validators.trailing_newline(line)

        self.assertIsNone(res)

    def test_trailing_whitespace_failed(self):
        line = ['line1', 'line2', 'line3    ']
        res = validators.trailing_whitespace(line)

        self.assertTrue(res)

    def test_trailing_whitespace_failed_multiline(self):
        line = ['line1', 'line2    ', 'line3', 'line4    ']
        res = validators.trailing_whitespace(line)

        self.assertItemsEqual(res, [2, 4])

    def test_trailing_whitespace_success(self):
        line = ['line1', 'line2', 'line3']
        res = validators.trailing_whitespace(line)

        self.assertIsNone(res)

    @patch('molecule.validators.rubocop')
    def test_rubocop(self, mocked):
        args = ['/tmp']
        kwargs = {'pattern': '**/**/**/*', 'out': '/dev/null', 'err': None}
        validators.rubocop(*args, **kwargs)
        mocked.assert_called_once_with(*args, **kwargs)

    @patch('molecule.validators.rake')
    def test_rake(self, mocked):
        args = ['/tmp/rakefile']
        kwargs = {'debug': True, 'out': None, 'err': '/dev/null'}
        validators.rake(*args, **kwargs)
        mocked.assert_called_once_with(*args, **kwargs)

    @patch('molecule.validators.testinfra')
    def test_testinfra(self, mocked):
        args = ['/tmp/ansible-inventory']
        kwargs = {'debug': True, 'out': None, 'err': None}
        validators.testinfra(*args, **kwargs)
        mocked.assert_called_once_with(*args, **kwargs)
