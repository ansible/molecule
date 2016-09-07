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

import pytest
import vagrant

from molecule.command import converge
from molecule.command import create
from molecule.command import destroy

pytestmark = pytest.mark.skipif(
    vagrant.get_vagrant_executable() is None,
    reason='No vagrant executable found - skipping vagrant tests')


@pytest.fixture()
def command_args(request):
    return []


@pytest.fixture()
def args(request):
    return {'--help': False, '--version': False, '<command>': 'create'}


@pytest.fixture()
def teardown(request):
    def cleanup():
        try:
            des = destroy.Destroy([], [])
            des.execute()
        except SystemExit:
            pass

    request.addfinalizer(cleanup)


def test_vagrant_create(molecule_file, command_args, args, teardown):
    c = create.Create(command_args, args)

    try:
        c.execute()
    except SystemExit as f:
        assert f.code == 0


def test_vagrant_converge(molecule_file, command_args, args, teardown):
    c = converge.Converge(command_args, args)

    try:
        c.execute()
    except SystemExit as f:
        assert f.code == 0
