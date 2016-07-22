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

import subprocess

from molecule import utilities
from molecule.commands import base


class Destroy(base.BaseCommand):
    """
    Destroys all instances created by molecule.

    Usage:
        destroy [--platform=<platform>] [--provider=<provider>] [--debug]

    Options:
        --platform=<platform>  specify a platform
        --provider=<provider>  specify a provider
        --debug                get more detail
    """

    def execute(self, exit=True):
        """
        Removes template files.
        Clears state file of all info (default platform).

        :return: None
        """
        self.molecule._create_templates()
        try:
            utilities.print_info("Destroying instances ...")
            self.molecule._provisioner.destroy()
            self.molecule._state.reset()
        except subprocess.CalledProcessError as e:
            utilities.logger.error('ERROR: {}'.format(e))
            if exit:
                utilities.sysexit(e.returncode)
            return e.returncode, e.message
        self.molecule._remove_templates()
        self.molecule._remove_inventory_file()
        return None, None
