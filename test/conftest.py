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

import distutils.spawn
import distutils.version
import logging
import os
import random
import shutil
import string

import ansible
import pytest

logging.getLogger("sh").setLevel(logging.WARNING)

pytest_plugins = ['helpers_namespace']


@pytest.helpers.register
def random_string(l=5):
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(l))


@pytest.fixture()
def temp_dir(tmpdir, request):
    d = tmpdir.mkdir(random_string())
    os.chdir(d.strpath)

    def cleanup():
        shutil.rmtree(d.strpath)

    request.addfinalizer(cleanup)

    return d.strpath


def ansible_v1():
    d = distutils.version
    return (d.LooseVersion(ansible.__version__) < d.LooseVersion('2.0'))


def get_docker_executable():
    not distutils.spawn.find_executable('docker')


def get_vagrant_executable():
    not distutils.spawn.find_executable('vagrant')


@pytest.helpers.register
def supports_docker():
    return pytest.mark.skipif(
        ansible_v1() or get_docker_executable(), reason='Docker not supported')


@pytest.helpers.register
def supports_vagrant():
    return pytest.mark.skipif(
        get_vagrant_executable(), reason='Vagrant not supported')
