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

import StringIO

import testtools
from testtools.matchers import MatchesRegex
from docopt import DocoptExit
from mock import patch

from molecule.cli import CLI


class TestCLI(testtools.TestCase):
    def setUp(self):
        super(TestCLI, self).setUp()
        self._cli = CLI()

    def test_cli_raises_usage_without_arguments(self):
        self.assertRaises(DocoptExit, lambda: self._cli.main())

    def test_cli_prints_version(self):
        with patch('sys.argv', ['bin/molecule', '--version']):
            with patch('sys.stdout', StringIO.StringIO()) as mocked_stdout:
                result = self.assertRaises(SystemExit, lambda: self._cli.main())
                stdout = mocked_stdout.getvalue().strip()

                self.assertEqual(result.code, None)
                self.assertThat(stdout, MatchesRegex('^\d\.\d\.\d'))

    def test_cli_raises_usage_with_invalid_sub_command(self):
        with patch('sys.argv', ['bin/molecule', 'invalid-subcommand']):
            self.assertRaises(DocoptExit, lambda: self._cli.main())
