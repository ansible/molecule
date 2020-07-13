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
"""Provisioner Ansible Plugins."""

import os

from molecule import config, interpolation, util


def from_yaml(data):
    """
    Interpolate the provided data and return a dict.

    Currently, this is used to reinterpolate the `molecule.yml` inside an
    Ansible playbook.  If there were any interpolation errors, they would
    have been found and raised earlier.

    :return: dict
    """
    molecule_env_file = os.environ["MOLECULE_ENV_FILE"]

    env = os.environ.copy()
    env = config.set_env_from_file(env, molecule_env_file)

    i = interpolation.Interpolator(interpolation.TemplateWithDefaults, env)
    interpolated_data = i.interpolate(data)

    return util.safe_load(interpolated_data)


def to_yaml(data):
    """Format data as YAML."""
    return str(util.safe_dump(data))


def header(content):
    """Return heaader to be added."""
    return util.molecule_prepender(content)


def get_docker_networks(data, state, labels={}):
    """Get list of docker networks."""
    network_list = []
    network_names = []
    for platform in data:
        if "docker_networks" in platform:
            for docker_network in platform["docker_networks"]:
                if "labels" not in docker_network:
                    docker_network["labels"] = {}
                for key in labels:
                    docker_network["labels"][key] = labels[key]

                docker_network["state"] = state

                if "name" in docker_network:
                    network_list.append(docker_network)
                    network_names.append(docker_network["name"])

        # If a network name is defined for a platform but is not defined in
        # docker_networks, add it to the network list.
        if "networks" in platform:
            for network in platform["networks"]:
                if "name" in network:
                    name = network["name"]
                    if name not in network_names:
                        network_list.append(
                            {"name": name, "labels": labels, "state": state}
                        )
    return network_list


class FilterModule(object):
    """Core Molecule filter plugins."""

    def filters(self):
        return {
            "molecule_from_yaml": from_yaml,
            "molecule_to_yaml": to_yaml,
            "molecule_header": header,
            "molecule_get_docker_networks": get_docker_networks,
        }
