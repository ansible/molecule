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

import sys

import sh

from provisioners import Ansible


class Commands(object):
    def __init__(self, args):
        self.args = args

    def main(self):
        self.molecule = Ansible(self.args)
        self.molecule.main()

        if self.molecule._provider in ['virtualbox', 'openstack']:
            self.commands = BaseCommands(self.molecule)

        if self.molecule._provider is 'metal':
            self.commands = MetalCommands(self.molecule)

    def destroy(self):
        self.commands.destroy()

    def create(self):
        self.commands.create()

    def converge(self):
        self.molecule.converge()


class BaseCommands(object):
    def __init__(self, molecule):
        self.molecule = molecule

    def destroy(self):
        self.molecule._create_templates()
        try:
            self.molecule._vagrant.halt()
            self.molecule._vagrant.destroy()
            self.molecule._set_default_platform(platform=False)
        except CalledProcessError as e:
            print('ERROR: {}'.format(e))
            sys.exit(e.returncode)
        self.molecule._remove_templates()

    def create(self):
        self.molecule._create_templates()
        if not self.molecule._created:
            try:
                self.molecule._vagrant.up(no_provision=True)
                self.molecule._created = True
            except CalledProcessError as e:
                print('ERROR: {}'.format(e))
                sys.exit(e.returncode)

    def converge(self, idempotent=False):
        if not idempotent:
            self.create()

        self.molecule._create_inventory_file()
        playbook, args, kwargs = self.molecule._create_playbook_args()
        print playbook


        # if idempotent:
        #     kwargs.pop('_out', None)
        #     kwargs.pop('_err', None)
        #     kwargs['_env']['ANSIBLE_NOCOLOR'] = 'true'
        #     kwargs['_env']['ANSIBLE_FORCE_COLOR'] = 'false'
        #     try:
        #         output = sh.ansible_playbook(playbook, *args, **kwargs)
        #         return output
        #     except sh.ErrorReturnCode as e:
        #         print('ERROR: {}'.format(e))
        #         sys.exit(e.exit_code)
        # try:
        #     output = sh.ansible_playbook(playbook, *args, **kwargs)
        #     return output.exit_code
        # except sh.ErrorReturnCode as e:
        #     print('ERROR: {}'.format(e))
        #     sys.exit(e.exit_code)


class MetalCommands(BaseCommands):
    def __init__(self, molecule):
        super(self.__class__, self).__init__(molecule)
