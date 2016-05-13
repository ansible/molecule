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

from molecule.ansible_galaxy_install import AnsibleGalaxyInstall


class TestConfig(testtools.TestCase):
    def setUp(self):
        super(TestConfig, self).setUp()

        self.data = {
            'config_file': 'test.cfg',
            'requirements_file': 'requirements.yml'
        }

        self.galaxy_install = AnsibleGalaxyInstall(self.data[
            'requirements_file'])

    def test_requirements_file_loading(self):
        self.assertEqual(self.galaxy_install.requirements_file,
                         self.data['requirements_file'])

    def test_add_env_arg(self):
        self.galaxy_install.add_env_arg('MOLECULE_1', 'test')
        self.assertEqual(self.galaxy_install.env['MOLECULE_1'], 'test')
