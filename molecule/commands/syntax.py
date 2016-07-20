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

from molecule import ansible_playbook
from molecule import utilities
from molecule.commands import base


class Syntax(base.BaseCommand):
    """
    Performs a syntax check on the current role.

    Usage:
        syntax
    """

    def execute(self, exit=True):
        self.molecule._create_templates()

        ansible = ansible_playbook.AnsiblePlaybook(
            self.molecule._config.config['ansible'])
        ansible.add_cli_arg('syntax-check', True)
        ansible.add_cli_arg('inventory-file', 'localhost,')

        utilities.print_info("Checking playbooks syntax ...")

        return ansible.execute(hide_errors=True)
