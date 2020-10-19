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


@pytest.fixture
def command_patched_ansible_create(mocker):
    return mocker.patch("molecule.provisioner.ansible.Ansible.create")


@pytest.fixture
def command_driver_delegated_section_data():
    x = {
        "driver": {
            "name": "delegated",
            "options": {
                "managed": False,
                # "login_cmd_template": "docker exec -ti {instance} bash",
                # "ansible_connection_options": {"ansible_connection": "docker"},
            },
        }
    }
    # if "DOCKER_HOST" in os.environ:
    #     x["driver"]["options"]["ansible_docker_extra_args"] = "-H={}".format(
    #         os.environ["DOCKER_HOST"]
    #     )
    return x


@pytest.fixture
def command_driver_delegated_managed_section_data():
    return {"driver": {"name": "delegated", "managed": True}}
