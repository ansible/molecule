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

from molecule.commands.create import Create
from molecule.commands.converge import Converge

import logging

logging.getLogger("sh").setLevel(logging.WARNING)

@pytest.fixture()
def molecule_file(tmpdir, request):
    d = tmpdir.mkdir('molecule')
    c = d.join(os.extsep.join(('molecule', 'yml')))
    data = {
        'molecule': {
            'molecule_dir': '.molecule'
        },
        'vagrant': {
            'platforms': [
                {'name': 'ubuntu',
                 'box': 'ubuntu/trusty64'}
            ],
            'providers': [
                {'name': 'virtualbox',
                 'type': 'virtualbox'}
            ],
            'instances': [
                {'name': 'aio-01'}
            ]
        },
        'ansible': {
            'config_file': 'test_config',
            'inventory_file': 'test_inventory',
        }
    }
    c.write(data)

    pbook = d.join(os.extsep.join(('playbook','yml')))
    data = [
        {'hosts': 'all',
        'tasks': [
            {'command': 'echo'}
        ]
         }
    ]

    pbook.write(data)

    os.chdir(d.strpath)



    def cleanup():
        os.chdir(os.path.join(d.strpath, '.molecule'))
        v = vagrant.Vagrant(os.path.abspath(os.curdir), quiet_stdout=False, quiet_stderr=False)
        v.destroy()
        os.remove(c.strpath)
        shutil.rmtree(d.strpath)

    request.addfinalizer(cleanup)

    return c.strpath


def test_vagrant_create(molecule_file):
    assert os.path.isfile(molecule_file)
    c = Create([], [])

    try:
        c.execute()
    except SystemExit as f:
        assert f.code == 0

    assert os.path.isdir('.vagrant')

def test_vagrant_converge(molecule_file):
    assert os.path.isfile(molecule_file)
    c = Converge([], [])

    try:
        c.execute()
    except SystemExit as f:
        assert f.code == 0

    assert os.path.isdir('.vagrant')
