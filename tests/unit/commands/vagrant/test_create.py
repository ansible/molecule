#  Copyright (c) 2015-2016 Cisco Systems
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
import shutil

import pytest
import vagrant
import yaml

from molecule.commands import converge
from molecule.commands import create
from molecule.commands import destroy

pytestmark = pytest.mark.skipif(
    vagrant.get_vagrant_executable() is None,
    reason='No vagrant executable found - skipping vagrant tests')


@pytest.fixture()
def molecule_file(tmpdir, request, molecule_vagrant_config):
    d = tmpdir.mkdir('molecule')
    c = d.join(os.extsep.join(('molecule', 'yml')))
    data = molecule_vagrant_config
    c.write(data)

    pbook = d.join(os.extsep.join(('playbook', 'yml')))
    data = [{'hosts': 'all', 'tasks': [{'command': 'echo'}]}]
    pbook.write(yaml.safe_dump(data))

    os.chdir(d.strpath)

    def cleanup():
        try:
            des = destroy.Destroy([], [])
            des.execute()
        except SystemExit:
            pass
        os.remove(c.strpath)
        shutil.rmtree(d.strpath)

    request.addfinalizer(cleanup)

    return c.strpath


def test_vagrant_create(molecule_file):
    c = create.Create([], [])

    try:
        c.execute()
    except SystemExit as f:
        assert f.code == 0


def test_vagrant_converge(molecule_file):
    c = converge.Converge([], [])

    try:
        c.execute()
    except SystemExit as f:
        assert f.code == 0
