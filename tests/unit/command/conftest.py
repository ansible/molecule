#  Copyright (c) 2015-2018 Cisco Systems, Inc.  # noqa: D100
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
from __future__ import annotations

import pytest


@pytest.fixture
def command_patched_ansible_create(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    return mocker.patch("molecule.provisioner.ansible.Ansible.create")


@pytest.fixture
def command_driver_delegated_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    x = {
        "driver": {
            "name": "default",
            "options": {
                "managed": False,
            },
        },
    }
    # if "DOCKER_HOST" in os.environ:
    #     x["driver"]["options"]["ansible_docker_extra_args"] = "-H={}".format(
    return x  # noqa: RET504


@pytest.fixture
def command_driver_delegated_managed_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    return {"driver": {"name": "default", "managed": True}}
