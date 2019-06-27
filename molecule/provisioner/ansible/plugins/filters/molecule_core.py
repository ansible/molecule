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

import os

from ansible import __version__ as ansible_version
from ansible.plugins.test.core import version_compare
from molecule import config
from molecule import interpolation
from molecule import util


def from_yaml(data):
    """
    Interpolate the provided data and return a dict.

    Currently, this is used to reinterpolate the `molecule.yml` inside an
    Ansible playbook.  If there were any interpolation errors, they would
    have been found and raised earlier.

    :return: dict
    """
    molecule_env_file = os.environ['MOLECULE_ENV_FILE']

    env = os.environ.copy()
    env = config.set_env_from_file(env, molecule_env_file)

    i = interpolation.Interpolator(interpolation.TemplateWithDefaults, env)
    interpolated_data = i.interpolate(data)

    return util.safe_load(interpolated_data)


def to_yaml(data):
    return str(util.safe_dump(data))


def header(content):
    return util.molecule_prepender(content)


def get_docker_networks(data):
    network_list = []
    for platform in data:
        if "networks" in platform:
            for network in platform['networks']:
                if "name" in network:
                    name = network['name']
                    network_list.append(name)
    return network_list


def get_docker_network_configs(data):
    network_config_list = []
    # docker_network module uses ipam_config starting with
    # ansible 2.8, ipam_options for older versions
    ipam_config_key = 'ipam_config' if version_compare(
        ansible_version, '2.8', operator='ge') else 'ipam_options'
    for platform in data:
        if "networks" in platform:
            for network in platform['networks']:
                if "name" in network:
                    network_config = {
                        'name': network['name'],
                    }

                    if "ipam_config" in network or "ipam_options" in network:
                        network_config.update({
                            ipam_config_key: network.get(
                                'ipam_config',
                                network.get('ipam_options')),
                        })

                    network_config_list.append(network_config)
    return network_config_list


def get_docker_container_networks(platform):
    if "networks" in platform:
        networks = []
        for network in platform['networks']:
            if "name" in network:
                if "ipam_config" in network:
                    del network["ipam_config"]

                if "ipam_options" in network:
                    del network["ipam_options"]

                networks.append(network)
        return networks
    return None


class FilterModule(object):
    """ Core Molecule filter plugins. """

    def filters(self):
        return {
            'molecule_from_yaml': from_yaml,
            'molecule_to_yaml': to_yaml,
            'molecule_header': header,
            'molecule_get_docker_networks': get_docker_networks,
            'molecule_get_docker_network_configs': get_docker_network_configs,
            'molecule_get_docker_container_networks':
                get_docker_container_networks,
        }
