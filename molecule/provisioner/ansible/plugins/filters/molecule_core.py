#  Copyright (c) 2015-2017 Cisco Systems, Inc.
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
    i = interpolation.Interpolator(interpolation.TemplateWithDefaults,
                                   os.environ)
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


class FilterModule(object):
    """ Core Molecule filter plugins. """

    def filters(self):
        return {
            'molecule_from_yaml': from_yaml,
            'molecule_to_yaml': to_yaml,
            'molecule_header': header,
            'molecule_get_docker_networks': get_docker_networks,
        }
