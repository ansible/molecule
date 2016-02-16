#  Copyright (c) 2015 Cisco Systems
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

import os

import anyconfig
import testtools

import molecule.config as config


class TestConfig(testtools.TestCase):
    def setUp(self):
        super(TestConfig, self).setUp()
        self._config = config.Config()

    def test_load(self):
        assert isinstance(self._config.config, dict)

    def test_validate_schema(self):
        defaults_file = os.path.join(os.path.dirname(__file__), '../molecule/conf/defaults.yml')
        schema = os.path.join(os.path.dirname(__file__), 'support/molecule-schema.yml')
        (rc, _) = anyconfig.validate(anyconfig.load(defaults_file), anyconfig.load(schema))

        assert rc

    def test_build_easy_paths(self):
        self.assertEqual(self._config.config['molecule']['state_file'], os.path.join('.molecule', 'state'))
        self.assertEqual(self._config.config['molecule']['vagrantfile_file'], os.path.join('.molecule', 'vagrantfile'))
        self.assertEqual(self._config.config['molecule']['rakefile_file'], os.path.join('.molecule', 'rakefile'))
        self.assertEqual(self._config.config['molecule']['config_file'], os.path.join('.molecule', 'ansible.cfg'))
        self.assertEqual(self._config.config['molecule']['inventory_file'], os.path.join('.molecule',
                                                                                         'ansible_inventory'))

    def test_update_ansible_defaults(self):
        configs = [
            os.path.join(
                os.path.dirname(__file__), 'support/molecule.yml'), os.path.join(
                    os.path.dirname(__file__), '../molecule/conf/defaults.yml')
        ]
        c = config.Config(configs)
        self.assertEqual(c.config['ansible']['inventory_file'], 'test_inventory')
        self.assertEqual(c.config['ansible']['config_file'], 'test_config')

    def test_populate_instance_names(self):
        configs = [
            os.path.join(
                os.path.dirname(__file__), 'support/molecule.yml'), os.path.join(
                    os.path.dirname(__file__), '../molecule/conf/defaults.yml')
        ]
        c = config.Config(configs)
        c._populate_instance_names('rhel-7')

        self.assertEqual(c.config['vagrant']['instances'][0]['vm_name'], 'aio-01-rhel-7')
