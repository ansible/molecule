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

import os

import sh
import testtools

import molecule.validators as validators


class TestValidators(testtools.TestCase):
    def setUp(self):
        super(TestValidators, self).setUp()
        self.good_path = '/tmp/test_validators_good/'
        self.bad_path = '/tmp/test_validators_bad/'
        self.good_file = 'good_ruby.rb'
        self.bad_file = 'bad_ruby.rb'
        good_ruby = "myvar = 'foo'\nputs myvar\n"
        bad_ruby = 'myvar = "foo"'

        if not os.path.exists(self.good_path):
            os.makedirs(self.good_path)
        with open(self.good_path + self.good_file, 'w') as f:
            f.write(good_ruby)

        if not os.path.exists(self.bad_path):
            os.makedirs(self.bad_path)
        with open(self.bad_path + self.bad_file, 'w') as f:
            f.write(bad_ruby)

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

    def test_rubocop_good_ruby(self):
        result = validators.rubocop(self.good_path, out='/dev/null', err='/dev/null')
        self.assertEqual(result.exit_code, 0)

    def test_rubocop_bad_ruby(self):
        self.assertRaises(sh.ErrorReturnCode_1, validators.rubocop, self.bad_path, out='/dev/null', err='/dev/null')

    def tearDown(self):
        super(TestValidators, self).tearDown()
        os.remove(self.good_path + self.good_file)
        os.remove(self.bad_path + self.bad_file)
        os.rmdir(self.good_path)
        os.rmdir(self.bad_path)
