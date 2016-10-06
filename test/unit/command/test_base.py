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

from molecule.command import base


class Foo(base.Base):
    def execute(self, exit=True):
        pass


def test_main(mocker, molecule_instance):
    patched_file_exists = mocker.patch(
        'molecule.config.Config.molecule_file_exists')
    patched_molecule_main = mocker.patch('molecule.core.Molecule.main')
    patched_file_exists.return_value = True

    foo = Foo({}, {}, molecule_instance)
    foo.main()

    patched_molecule_main.assert_called_once()


def test_main_exits_when_missing_config(patched_logger_error,
                                        molecule_instance):
    foo = Foo({}, {}, molecule_instance)
    with pytest.raises(SystemExit):
        foo.main()

    msg = 'Unable to find molecule.yml. Exiting.'
    patched_logger_error.assert_called_once_with(msg)
