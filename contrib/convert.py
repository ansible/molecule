#!/usr/bin/env python
#
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

import argparse
import collections
import errno
import glob
import os
import shutil

import yaml

from molecule import logger
from molecule import util

parser = argparse.ArgumentParser()
parser.add_argument('old_molecule_file')
args = parser.parse_args()

_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG

LOG = logger.get_logger(__name__)


def dict_representer(dumper, data):
    return dumper.represent_dict(data.iteritems())


def dict_constructor(loader, node):
    return collections.OrderedDict(loader.construct_pairs(node))


yaml.add_representer(collections.OrderedDict, dict_representer)
yaml.add_constructor(_mapping_tag, dict_constructor)


class MyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)


d = collections.OrderedDict({
    'dependency': {
        'name': 'galaxy',
    },
    'driver': {
        'name': 'vagrant',
    },
    'lint': {
        'name': 'ansible-lint',
    },
    'provisioner': collections.OrderedDict({}),
    'platforms': [],
    'scenario': {
        'name': 'default',
    },
    'verifier': {
        'name': 'testinfra',
    },
})

d['provisioner']['name'] = 'ansible'
d['provisioner']['env'] = collections.OrderedDict({})
d['provisioner']['env']['ANSIBLE_ROLES_PATH'] = '../../../../../'
d['provisioner']['env']['ANSIBLE_LIBRARY'] = '../../../../library'
d['provisioner']['env'][
    'ANSIBLE_LOOKUP_PLUGINS'] = '../../../../plugins/lookups'
d['provisioner']['env'][
    'ANSIBLE_FILTER_PLUGINS'] = '../../../../plugins/filters'
d['provisioner']['playbooks'] = collections.OrderedDict({})
d['provisioner']['playbooks'][
    'setup'] = '../../../../.molecule/playbooks/vagrant/create.yml'
d['provisioner']['playbooks'][
    'teardown'] = '../../../../.molecule/playbooks/vagrant/destroy.yml'
d['provisioner']['options'] = collections.OrderedDict({})
d['provisioner']['options']['become'] = True

old_molecule_file = args.old_molecule_file

if not os.path.isfile(old_molecule_file):
    msg = 'Unable to find {}. Exiting.'.format(old_molecule_file)
    util.sysexit_with_message(msg)

with open(old_molecule_file, 'r') as stream:
    y = yaml.load(stream)

    # PLATFORMS

    platforms = y['vagrant']['platforms'][0]
    box = platforms.get('box')
    box_version = platforms.get('box_version')
    box_url = platforms.get('box_url')

    # PROVIDERS

    providers = y['vagrant']['providers'][0]
    memory = providers.get('options').get('memory')

    # INSTANCES

    instances = y['vagrant']['instances']
    platforms = []
    for instance in instances:
        name = instance['name']
        groups = instance.get('ansible_groups')
        interfaces = instance.get('interfaces')

        i = collections.OrderedDict({})
        i['name'] = name
        if box:
            i['box'] = box

        if box_version:
            i['box_version'] = box_version

        if box_url:
            i['box_url'] = box_url

        if memory:
            i['memory'] = memory

        if groups:
            i['groups'] = groups

        if interfaces:
            i['interfaces'] = interfaces

        platforms.append(i)

    d.update({'platforms': platforms})

    od = collections.OrderedDict(sorted(d.items(), key=lambda t: t[0]))

    s = yaml.dump(
        od,
        Dumper=MyDumper,
        default_flow_style=False,
        explicit_start=True,
        line_break=1)

    old_role_dir = os.path.join(os.path.dirname(old_molecule_file))
    old_dot_molecule_dir = os.path.join(old_role_dir, '.molecule')
    old_test_dir = os.path.join(old_role_dir, 'tests')
    old_playbook = os.path.join(old_role_dir, 'playbook.yml')
    molecule_dir = os.path.join(old_role_dir, 'molecule')
    scenario_dir = os.path.join(molecule_dir, 'default')
    test_dir = os.path.join(scenario_dir, 'tests')
    molecule_file = os.path.join(scenario_dir, 'molecule.yml')

    dirs = [
        molecule_dir,
        scenario_dir,
        test_dir,
    ]
    for d in dirs:
        if not os.path.isdir(d):
            msg = 'Creating {}'.format(d)
            LOG.info(msg)
            os.mkdir(d)

    with open(molecule_file, 'w') as stream:
        msg = 'Writing molecule.yml to {}'.format(molecule_file)
        LOG.info(msg)
        stream.write(s)

    for f in glob.glob(r'{}/test_*.py'.format(old_test_dir)):
        msg = 'Copying {} to {}'.format(f, test_dir)
        LOG.info(msg)
        shutil.copy(f, test_dir)

    if not os.path.isfile(old_playbook):
        msg = 'Copying {} to {}'.format(old_playbook, scenario_dir)
        LOG.info(msg)
        shutil.copy(old_playbook, scenario_dir)

    files = [
        old_dot_molecule_dir,
        old_molecule_file,
        old_playbook,
    ]
    for f in files:
        if os.path.exists(f):
            msg = 'Deleting {}'.format(f)
            LOG.warn(msg)
            try:
                shutil.rmtree(f)
            except OSError as exc:
                if exc.errno == errno.ENOTDIR:
                    os.remove(f)
                else:
                    raise
