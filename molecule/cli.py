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
"""
Usage:
    molecule [-hvm] <command> [<args>]

Commands:
    create      create instances
    converge    create and provision instances
    idempotence converge and check the output for changes
    test        run a full test cycle: destroy, create, converge, idempotency-check, verify and destroy instances
    verify      create, provision and test instances
    destroy     destroy instances
    status      show status of instances
    list        show available platforms, providers
    login       connects to instance via SSH
    init        creates the directory structure and files for a new Ansible role compatible with molecule

Options:
   -h, --help             shows this screen
   -v, --version          shows the version
   -m                     machine readable output
"""
# molecule [-hvm] [--platform=<platform>] [--provider=<provider>] [--tags=<tag1,tag2>] [--debug] <command> [<args>]
import sys

from docopt import docopt
from docopt import DocoptExit

import molecule
import molecule.commands as commands


class CLI(object):
    def main(self):
        args = docopt(__doc__, version=molecule.__version__, options_first=True)

        command_name = args.pop('<command>').capitalize()
        command_args = args.pop('<args>')
        if command_args is None:
            command_args = {}

        try:
            command_class = getattr(commands, command_name)
        except AttributeError:
            raise DocoptExit()

        command = command_class(command_args, args)
        sys.exit(command.execute())


def main():
    CLI().main()


if __name__ == '__main__':
    main()
