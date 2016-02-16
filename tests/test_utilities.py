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

import binascii
import os
import StringIO

import testtools
from mock import patch

import molecule.utilities as utilities


class TestUtilities(testtools.TestCase):
    def setUp(self):
        super(TestUtilities, self).setUp()

    def test_write_template(self):
        tmp_file = '/tmp/test_utilities_write_template.tmp'
        utilities.write_template('test_write_template.j2', tmp_file, {'test': 'chicken'}, _dir='templates/tests')
        with open(tmp_file, 'r') as f:
            data = f.read()
        os.remove(tmp_file)

        self.assertEqual(data, 'this is a chicken\n')

    def test_write_file(self):
        tmp_file = '/tmp/test_utilities_write_file.tmp'
        contents = binascii.b2a_hex(os.urandom(15))
        utilities.write_file(tmp_file, contents)
        with open(tmp_file, 'r') as f:
            data = f.read()
        os.remove(tmp_file)

        self.assertEqual(data, contents)

    def test_print_stdout(self):
        with patch('sys.stdout', StringIO.StringIO()) as mocked_stdout:
            utilities.print_stdout('test stdout')
            stdout = mocked_stdout.getvalue()

            self.assertEqual(stdout, 'test stdout')

    def test_print_stderr(self):
        with patch('sys.stderr', StringIO.StringIO()) as mocked_stderr:
            utilities.print_stderr('test stderr')
            stderr = mocked_stderr.getvalue()

            self.assertEqual(stderr, 'test stderr')

    def test_format_instance_name_00(self):
        instances = [{'name': 'test-01'}]
        expected = None
        actual = utilities.format_instance_name('test-02', 'rhel-7', instances)
        self.assertEqual(expected, actual)

    def test_format_instance_name_01(self):
        instances = [{'name': 'test-01'}]
        expected = 'test-01-rhel-7'
        actual = utilities.format_instance_name('test-01', 'rhel-7', instances)
        self.assertEqual(expected, actual)

    def test_format_instance_name_02(self):
        instances = [{'name': 'test-01', 'options': {'append_platform_to_hostname': False}}]
        expected = 'test-01'
        actual = utilities.format_instance_name('test-01', 'rhel-7', instances)
        self.assertEqual(expected, actual)

    def test_format_instance_name_03(self):
        instances = [{'name': 'test-01', 'options': {'chicken': False}}]
        expected = 'test-01-rhel-7'
        actual = utilities.format_instance_name('test-01', 'rhel-7', instances)
        self.assertEqual(expected, actual)
