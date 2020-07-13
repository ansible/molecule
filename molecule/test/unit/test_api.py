#  Copyright (c) 2019 Red Hat, Inc.
#  Copyright (c) 2015-2018 Cisco Systems, Inc.
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
import sh

from molecule import api


def test_api_molecule_drivers_as_attributes():
    results = api.drivers()
    assert hasattr(results, "delegated")
    assert isinstance(results.delegated, api.Driver)


def test_api_drivers():
    results = api.drivers()

    for result in results:
        assert isinstance(result, api.Driver)

    assert "delegated" in results


def test_api_verifiers():
    x = ["testinfra", "ansible"]

    assert all(elem in api.verifiers() for elem in x)


def test_cli_mol():
    cmd_molecule = sh.molecule.bake("--version")
    x = pytest.helpers.run_command(cmd_molecule, log=False)
    cmd_mol = sh.mol.bake("--version")
    y = pytest.helpers.run_command(cmd_mol, log=False)
    assert x.exit_code == y.exit_code
    assert x.stderr == y.stderr
    assert x.stdout == y.stdout
