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

import testtools

import molecule.provisioners as provisioners
from molecule.core import Molecule
import yaml
from molecule.ansible_playbook import AnsiblePlaybook


class TestDockerProvisioner(testtools.TestCase):
    def setUp(self):
        super(TestDockerProvisioner, self).setUp()
        # Setup mock molecule
        self._mock_molecule = Molecule(dict())

        self.temp = '/tmp/test_config_load_defaults_external_file.yml'
        data = {
            'molecule': {
                'molecule_dir': '.test_molecule',
                'inventory_file': 'tests/ansible_inventory'
            },
            'docker': {
                'containers': [
                    {'name': 'test1',
                     'image': 'ubuntu',
                     'image_version': 'latest',
                     'ansible_groups': ['group1']}, {'name': 'test2',
                                                     'image': 'ubuntu',
                                                     'image_version': 'latest',
                                                     'ansible_groups':
                                                     ['group2']}
                ]
            },
            'ansible': {
                'config_file': 'test_config',
                'inventory_file': 'test_inventory'
            }
        }

        with open(self.temp, 'w') as f:
            f.write(yaml.dump(data, default_flow_style=True))

        self._mock_molecule._config.load_defaults_file(defaults_file=self.temp)

        self._mock_molecule._state = dict()

    def test_name(self):
        docker_provisioner = provisioners.DockerProvisioner(
            self._mock_molecule)
        # false values don't exist in arg dict at all
        self.assertEqual(docker_provisioner.name, 'docker')

    def test_get_provisioner(self):
        self.assertEqual(
            provisioners.get_provisioner(self._mock_molecule).name, 'docker')

    def test_up(self):
        docker_provisioner = provisioners.DockerProvisioner(
            self._mock_molecule)
        docker_provisioner.up()
        docker_provisioner.destroy()

    def test_instances(self):
        docker_provisioner = provisioners.DockerProvisioner(
            self._mock_molecule)
        self.assertEqual(docker_provisioner.instances[0]['name'], 'test1')
        self.assertEqual(docker_provisioner.instances[1]['name'], 'test2')

    def test_status(self):
        docker_provisioner = provisioners.DockerProvisioner(
            self._mock_molecule)

        docker_provisioner.up()

        self.assertEquals('test1', docker_provisioner.status()[1].name)
        self.assertEquals('test2', docker_provisioner.status()[0].name)

        self.assertIn('Up', docker_provisioner.status()[1].state)
        self.assertIn('Up', docker_provisioner.status()[0].state)

        self.assertEqual('docker', docker_provisioner.status()[0].provider)
        self.assertEqual('docker', docker_provisioner.status()[1].provider)

    def test_destroy(self):
        docker_provisioner = provisioners.DockerProvisioner(
            self._mock_molecule)

        docker_provisioner.up()

        self.assertEquals('test1', docker_provisioner.status()[1].name)
        self.assertEquals('test2', docker_provisioner.status()[0].name)

        self.assertIn('Up', docker_provisioner.status()[1].state)
        self.assertIn('Up', docker_provisioner.status()[0].state)

        docker_provisioner.destroy()

        self.assertIn('Not Created', docker_provisioner.status()[1].state)
        self.assertIn('Not Created', docker_provisioner.status()[0].state)

    def test_provision(self):

        docker_provisioner = provisioners.DockerProvisioner(
            self._mock_molecule)
        docker_provisioner.destroy()
        docker_provisioner.up()

        self.book = docker_provisioner.ansible_connection_params
        self.book['playbook'] = 'tests/playbook.yml'
        self.book['inventory'] = 'test1,test2,'

        self.ansible = AnsiblePlaybook(self.book)

        self.assertEqual((None, ''), self.ansible.execute())

        docker_provisioner.destroy()

    def test_inventory_generation(self):
        self._mock_molecule._provisioner = provisioners.get_provisioner(
            self._mock_molecule)
        self._mock_molecule._provisioner.destroy()
        self._mock_molecule._provisioner.up()

        self._mock_molecule._create_inventory_file()

        self.book = self._mock_molecule._provisioner.ansible_connection_params
        self.book['playbook'] = 'tests/playbook.yml'
        self.book['inventory'] = 'tests/ansible_inventory'

        self.ansible = AnsiblePlaybook(self.book)

        self.assertEqual((None, ''), self.ansible.execute())
