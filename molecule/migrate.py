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

import collections
import json

import yaml

from molecule import logger
from molecule import util
from molecule.model import schema
from molecule.model import schema_v1

LOG = logger.get_logger(__name__)


class MyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)


class Migrate(object):
    def __init__(self, molecule_file):
        """
        Initialize a new migrate class and returns None.

        :param molecule_file: A string containing an absolute path to the
         molecule v1 config to parse.
        :return: None
        """
        self._molecule_file = molecule_file
        self._v2 = self._get_config()
        self._v1 = self._get_v1_config()

    def dump(self):
        od = self._convert()
        yaml.add_representer(collections.OrderedDict,
                             self._get_dict_representer)

        return yaml.dump(
            od,
            Dumper=MyDumper,
            default_flow_style=False,
            explicit_start=True,
            line_break=1)

    def _convert(self):
        if self._v1.get('vagrant'):
            msg = 'Vagrant syle v1 config found'
            LOG.info(msg)
            self._set_vagrant_platforms()
            self._set_vagrant_provider()
        else:
            msg = 'Vagrant migrations only supported.  Exiting.'
            util.sysexit_with_message(msg)

        self._set_provisioner()
        self._set_verifier()

        od = collections.OrderedDict(
            sorted(self._v2.items(), key=lambda t: t[0]))
        schema.validate(self._to_dict(od))

        return od

    def _to_dict(self, od):
        return json.loads(json.dumps(od))

    def _set_vagrant_provider(self):
        provider = self._v1['vagrant']['providers'][0]

        self._v2['driver']['provider']['name'] = provider['name']

    def _set_vagrant_platforms(self):
        platforms = self._v1['vagrant']['platforms'][0]
        provider = self._v1['vagrant']['providers'][0]

        platforms_list = []
        instances = self._v1['vagrant']['instances']
        for instance in instances:
            i = collections.OrderedDict({})
            i['name'] = instance['name']

            if platforms.get('box'):
                i['box'] = platforms['box']

            if platforms.get('box_version'):
                i['box_version'] = platforms['box_version']

            if platforms.get('box_url'):
                i['box_url'] = platforms['box_url']

            if provider.get('options', {}).get('memory'):
                i['memory'] = provider['options']['memory']

            if provider.get('options', {}).get('cpus'):
                i['cpus'] = provider['options']['cpus']

            if instance.get('ansible_groups'):
                i['groups'] = instance['ansible_groups']

            if instance.get('interfaces'):
                i['interfaces'] = instance['interfaces']

            if instance.get('raw_config_args'):
                i['raw_config_args'] = instance['raw_config_args']

            platforms_list.append(i)

        self._v2['platforms'] = platforms_list

    def _set_provisioner(self):
        ansible = self._v1.get('ansible', collections.OrderedDict({}))

        self._v2['provisioner']['name'] = 'ansible'
        self._v2['provisioner']['env'] = collections.OrderedDict({})

        if ansible.get('raw_env_vars'):
            self._v2['provisioner']['env'] = self._v1['ansible'][
                'raw_env_vars']

        self._v2['provisioner']['options'] = collections.OrderedDict({})
        self._v2['provisioner']['lint'] = collections.OrderedDict({})
        self._v2['provisioner']['lint']['name'] = 'ansible-lint'

        if ansible.get('extra_vars'):
            self._v2['provisioner']['options']['extra-vars'] = ansible[
                'extra_vars']

        if ansible.get('verbose'):
            self._v2['provisioner']['options']['verbose'] = ansible['verbose']

        if ansible.get('become'):
            self._v2['provisioner']['options']['become'] = ansible['become']

        if ansible.get('tags'):
            self._v2['provisioner']['options']['tags'] = ansible['tags']

    def _set_verifier(self):
        verifier = self._v1['verifier']

        self._v2['verifier']['name'] = 'testinfra'
        self._v2['verifier']['options'] = collections.OrderedDict({})
        self._v2['verifier']['lint'] = collections.OrderedDict({})
        self._v2['verifier']['lint']['name'] = 'flake8'

        if verifier.get('options', {}).get('sudo'):
            self._v2['verifier']['options']['sudo'] = verifier['options'][
                'sudo']

    def _get_dict_representer(self, dumper, data):
        return dumper.represent_dict(data.items())

    def _get_v1_config(self):
        d = util.safe_load(open(self._molecule_file))
        schema_v1.validate(d)

        return d

    def _get_config(self):
        d = collections.OrderedDict({
            'dependency': {
                'name': 'galaxy',
            },
            'driver': {
                'name': 'vagrant',
                'provider': collections.OrderedDict({}),
            },
            'lint': {
                'name': 'yamllint',
            },
            'provisioner':
            collections.OrderedDict({}),
            'platforms': [],
            'scenario': {
                'name': 'default',
            },
            'verifier':
            collections.OrderedDict({}),
        })

        return d
