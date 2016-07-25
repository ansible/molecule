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

import molecule.commands  # prevent circular dependencies
from molecule import utilities
from molecule.commands import base


class Test(base.BaseCommand):
    """
    Runs a series of commands (defined in config) against instances for a full test/verify run.

    Usage:
        test [--platform=<platform>] [--provider=<provider>] [--destroy=<destroy>] [--debug] [--sudo]

    Options:
        --platform=<platform>  specify a platform
        --provider=<provider>  specify a provider
        --destroy=<destroy>    destroy behavior (passing, always, never)
        --debug                get more detail
        --sudo                 run tests with sudo
    """

    def execute(self):
        command_args, args = utilities.remove_args(
            self.command_args, self.args, self.command_args)

        for task in self.molecule._config.config['molecule']['test'][
                'sequence']:
            command_module = getattr(molecule.commands, task)
            command = getattr(command_module, task.capitalize())
            c = command(command_args, args, self.molecule)

            for argument in self.command_args:
                if argument in c.args:
                    c.args[argument] = self.args[argument]

            status, output = c.execute(exit=False)

            # Fail fast
            if status is not 0 and status is not None:
                utilities.logger.error(output)
                utilities.sysexit(status)

        if self.args.get('--destroy') == 'always':
            c = molecule.commands.destroy.Destroy(command_args, args)
            c.execute()
            return None, None

        if self.args.get('--destroy') == 'never':
            return None, None

        # passing (default)
        if status is None:
            c = molecule.commands.destroy.Destroy(command_args, args)
            c.execute()
            return None, None

        # error encountered during test
        utilities.sysexit(status)
