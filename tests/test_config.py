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

import testtools
import yaml

import molecule.config as config


class TestConfig(testtools.TestCase):
    def setUp(self):
        super(TestConfig, self).setUp()

        self.temp = '/tmp/test_config_load_defaults_external_file.yml'
        data = {
            'molecule': {
                'molecule_dir': '.test_molecule'
            },
            'vagrant': {
                'instances': [
                    {'name': 'aio-01',
                     'options': {'append_platform_to_hostname': True}}
                ]
            },
            'ansible': {
                'config_file': 'test_config',
                'inventory_file': 'test_inventory'
            }
        }

        with open(self.temp, 'w') as f:
            f.write(yaml.dump(data, default_flow_style=True))

    def test_load_defaults_file(self):
        c = config.Config()
        c.load_defaults_file()

        self.assertEqual(c.config['molecule']['molecule_dir'], '.molecule')

    def test_load_defaults_external_file(self):
        c = config.Config()
        c.load_defaults_file(defaults_file=self.temp)

        self.assertEqual(c.config['molecule']['molecule_dir'],
                         '.test_molecule')

    def test_merge_molecule_config_files(self):
        c = config.Config()
        c.load_defaults_file()
        c.merge_molecule_config_files(paths=[self.temp])

        self.assertEqual(c.config['molecule']['molecule_dir'],
                         '.test_molecule')

    def test_merge_molecule_file(self):
        c = config.Config()
        c.load_defaults_file()
        c.merge_molecule_file(molecule_file=self.temp)

        self.assertEqual(c.config['molecule']['molecule_dir'],
                         '.test_molecule')

    def test_build_easy_paths(self):
        c = config.Config()
        c.load_defaults_file()
        c.build_easy_paths()

        self.assertEqual(c.config['molecule']['state_file'],
                         os.path.join('.molecule', 'state'))
        self.assertEqual(c.config['molecule']['vagrantfile_file'],
                         os.path.join('.molecule', 'vagrantfile'))
        self.assertEqual(c.config['molecule']['rakefile_file'],
                         os.path.join('.molecule', 'rakefile'))
        self.assertEqual(c.config['molecule']['config_file'],
                         os.path.join('.molecule', 'ansible.cfg'))
        self.assertEqual(c.config['molecule']['inventory_file'],
                         os.path.join('.molecule', 'ansible_inventory'))

    def test_update_ansible_defaults(self):
        c = config.Config()
        c.load_defaults_file()
        c.merge_molecule_file(molecule_file=self.temp)

        self.assertEqual(c.config['ansible']['inventory_file'],
                         'test_inventory')
        self.assertEqual(c.config['ansible']['config_file'], 'test_config')

    def test_populate_instance_names(self):
        c = config.Config()
        c.load_defaults_file()
        c.merge_molecule_file(molecule_file=self.temp)
        c.populate_instance_names('rhel-7')

        self.assertEqual(c.config['vagrant']['instances'][0]['vm_name'],
                         'aio-01-rhel-7')

    def tearDown(self):
        super(TestConfig, self).tearDown()
        os.remove(self.temp)
