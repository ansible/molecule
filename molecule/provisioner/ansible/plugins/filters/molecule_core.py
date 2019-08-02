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

    defaults = config.DEFAULTS.copy()
    if not isinstance(data, list):
        data = [data]
    for d in data:
        i = interpolation.Interpolator(interpolation.TemplateWithDefaults, env)
        interpolated_data = i.interpolate(d)
        defaults = util.merge_dicts(defaults, util.safe_load(interpolated_data))

    defaults = _parallelize_config(defaults)
    return defaults


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


def _parallelize_config(data):
    if 'platforms' not in data:
        return data
    state = util.safe_load_file(os.environ['MOLECULE_STATE_FILE'])
    if state.get('is_parallel', False):
        data['platforms'] = util._parallelize_platforms(data, state['run_uuid'])
    return data


class FilterModule(object):
    """ Core Molecule filter plugins. """

    def filters(self):
        return {
            'molecule_from_yaml': from_yaml,
            'molecule_to_yaml': to_yaml,
            'molecule_header': header,
            'molecule_get_docker_networks': get_docker_networks,
        }
