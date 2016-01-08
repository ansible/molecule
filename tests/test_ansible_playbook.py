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

from molecule.ansible_playbook import AnsiblePlaybook


class TestConfig(testtools.TestCase):
    def setUp(self):
        super(TestConfig, self).setUp()

        self.data = {
            'playbook': 'playbook.yml',
            'config_file': 'test.cfg',
            'limit': 'all',
            'verbose': 'vvvv',
            'diff': True,
            'host_key_checking': False,
            'raw_ssh_args': [
                '-o UserKnownHostsFile=/dev/null', '-o IdentitiesOnly=yes', '-o ControlMaster=auto',
                '-o ControlPersist=60s'
            ],
            'raw_env_vars': {
                'TEST_1': 'test_1'
            }
        }

        self.ansible = AnsiblePlaybook(self.data)

    def test_arg_loading(self):
        # string value set
        self.assertEqual(self.ansible.cli['limit'], self.data['limit'])

        # true value set
        self.assertEqual(self.ansible.cli['diff'], self.data['diff'])

        # false values don't exist in arg dict at all
        self.assertIsNone(self.ansible.cli.get('sudo_user'))

    def test_parse_arg_special_cases(self):
        # raw environment variables are set
        self.assertIsNone(self.ansible.cli.get('raw_env_vars'))
        self.assertEqual(self.ansible.env['TEST_1'], self.data['raw_env_vars']['TEST_1'])

        # raw_ssh_args set
        self.assertIsNone(self.ansible.cli.get('raw_ssh_args'))
        self.assertEqual(self.ansible.env['ANSIBLE_SSH_ARGS'], ' '.join(self.data['raw_ssh_args']))

        # host_key_checking gets set in environment as string 'false'
        self.assertIsNone(self.ansible.cli.get('host_key_checking'))
        self.assertEqual(self.ansible.env['ANSIBLE_HOST_KEY_CHECKING'], 'false')

        # config_file is set in environment
        self.assertIsNone(self.ansible.cli.get('config_file'))
        self.assertEqual(self.ansible.env['ANSIBLE_CONFIG'], self.data['config_file'])

        # playbook is set as attribute
        self.assertIsNone(self.ansible.cli.get('playbook'))
        self.assertEqual(self.ansible.playbook, self.data['playbook'])

        # verbose is set in the right place
        self.assertIsNone(self.ansible.cli.get('verbose'))
        self.assertIn('-' + self.data['verbose'], self.ansible.cli_pos)

    def test_add_cli_arg(self):
        # redefine a previously defined value
        self.ansible.add_cli_arg('limit', 'test')
        self.assertEqual(self.ansible.cli['limit'], 'test')

        # add a new value
        self.ansible.add_cli_arg('molecule_1', 'test')
        self.assertEqual(self.ansible.cli['molecule_1'], 'test')

        # values set as false shouldn't get added
        self.ansible.add_cli_arg('molecule_2', None)
        self.assertNotIn('molecule_2', self.ansible.cli)

    def test_remove_cli_arg(self):
        self.ansible.remove_cli_arg('limit')
        self.assertNotIn('limit', self.ansible.cli)

    def test_add_env_arg(self):
        # redefine a previously defined value
        self.ansible.add_env_arg('TEST_1', 'now')
        self.assertEqual(self.ansible.env['TEST_1'], 'now')

        # add a new value
        self.ansible.add_env_arg('MOLECULE_1', 'test')
        self.assertEqual(self.ansible.env['MOLECULE_1'], 'test')

    def test_remove_env_arg(self):
        self.ansible.remove_env_arg('TEST_1')
        self.assertNotIn('TEST_1', self.ansible.env)

    def test_bake(self):
        self.ansible.bake()
        self.assertIn('playbook.yml -vvvv --diff --limit=all', str(self.ansible.ansible))
