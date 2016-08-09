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

import pytest

from molecule import config
from molecule import core
from molecule import utilities


@pytest.fixture()
def molecule_args():
    return {'--debug': False,
            '--destroy': None,
            '--platform': None,
            '--provider': None,
            '--sudo': False,
            '<command>': 'test_command'}


@pytest.fixture()
def molecule_default_provider_instance(temp_files, molecule_args):
    c = temp_files(fixtures=['molecule_vagrant_config'])
    m = core.Molecule(molecule_args)
    m.config = config.Config(configs=c)
    m.main()

    return m


@pytest.fixture()
def molecule_invalid_provisioner_config(
        molecule_section_data, invalid_section_data, ansible_section_data):
    return reduce(
        lambda x, y: utilities.merge_dicts(x, y),
        [molecule_section_data, invalid_section_data, ansible_section_data])


@pytest.fixture()
def invalid_section_data():
    return {}
