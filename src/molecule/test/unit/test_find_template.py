# Copyright (c) 2013-2021, Audrey Roy Greenfeld
# All rights reserved.

# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:

# * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following
# disclaimer in the documentation and/or other materials provided
# with the distribution.

# * Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived
# from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Taken from Cookiecutter:
# https://github.com/cookiecutter/cookiecutter/blob/master/tests/test_find.py
import os

import pytest

from molecule.util import find_template


@pytest.fixture(params=["fake-repo-pre", "fake-repo-pre2"])
def repo_dir(request):
    """Fixture returning path for `test_find_template` test."""
    return os.path.join("src/molecule/test/unit", request.param)


def test_find_template(repo_dir):
    """Verify correctness of `find_template` path detection."""
    template = find_template(repo_dir=repo_dir)

    test_dir = os.path.join(repo_dir, "{{cookiecutter.repo_name}}")
    assert template == test_dir
