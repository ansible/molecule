#  Copyright (c) 2015-2016 Cisco Systems
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

import glob
import os

import sh

from molecule import ansible_playbook
from molecule import utilities
from molecule import validators
from molecule.commands import base

LOG = utilities.get_logger(__name__)


class Verify(base.BaseCommand):
    """
    Performs verification steps on running instances.

    Usage:
        verify [--platform=<platform>] [--provider=<provider>] [--debug] [--sudo]

    Options:
        --platform=<platform>  specify a platform
        --provider=<provider>  specify a provider
        --debug                get more detail
        --sudo                 runs tests with sudo
    """

    def execute(self, exit=True):
        serverspec_dir = self.molecule.config.config['molecule'][
            'serverspec_dir']
        testinfra_dir = self.molecule.config.config['molecule'][
            'testinfra_dir']
        rakefile = self.molecule.config.config['molecule']['rakefile_file']
        ignore_paths = self.molecule.config.config['molecule']['ignore_paths']

        # whitespace & trailing newline check
        validators.check_trailing_cruft(ignore_paths=ignore_paths, exit=exit)

        self.molecule._write_ssh_config()

        # testinfra's Ansible calls get same env vars as ansible-playbook
        ansible = ansible_playbook.AnsiblePlaybook(
            self.molecule.config.config['ansible'],
            _env=self.molecule._env)

        debug = self.molecule._args.get('--debug', False)

        testinfra_kwargs = utilities.merge_dicts(
            self.molecule._provisioner.testinfra_args,
            self.molecule.config.config['testinfra'])
        testinfra_kwargs['env'] = ansible.env
        testinfra_kwargs['env']['PYTHONDONTWRITEBYTECODE'] = '1'
        testinfra_kwargs['debug'] = debug
        testinfra_kwargs['sudo'] = self.molecule._args.get('--sudo', False)

        serverspec_kwargs = self.molecule._provisioner.serverspec_args
        serverspec_kwargs['debug'] = debug

        try:
            # testinfra
            tests = '{}/test_*.py'.format(testinfra_dir)
            tests_glob = glob.glob(tests)
            if len(tests_glob) > 0:
                msg = 'Executing testinfra tests found in {}/.'
                utilities.print_info(msg.format(testinfra_dir))
                validators.testinfra(tests_glob, **testinfra_kwargs)
            else:
                msg = 'No testinfra tests found in {}/.'
                LOG.warning(msg.format(testinfra_dir))

            # serverspec / rubocop
            if os.path.isdir(serverspec_dir):
                msg = 'Executing rubocop on *.rb files found in {}/.'
                utilities.print_info(msg.format(serverspec_dir))
                validators.rubocop(serverspec_dir, **serverspec_kwargs)

                msg = 'Executing serverspec tests found in {}/.'
                utilities.print_info(msg.format(serverspec_dir))
                validators.rake(rakefile, **serverspec_kwargs)
            else:
                msg = 'No serverspec tests found in {}/.'
                LOG.warning(msg.format(serverspec_dir))
        except sh.ErrorReturnCode as e:
            LOG.error('ERROR: {}'.format(e))
            if exit:
                utilities.sysexit(e.exit_code)
            return e.exit_code, e.stdout

        return None, None
