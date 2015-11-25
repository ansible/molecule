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
  molecule create      [--platform=<platform>] [--provider=<provider>] [--debug]
  molecule converge    [--platform=<platform>] [--provider=<provider>] [--tags=<tag1,tag2>] [--debug]
  molecule idempotence [--platform=<platform>] [--provider=<provider>] [--debug]
  molecule test        [--platform=<platform>] [--provider=<provider>] [--debug]
  molecule verify      [--platform=<platform>] [--provider=<provider>] [--debug]
  molecule destroy     [--platform=<platform>] [--provider=<provider>] [--debug]
  molecule status      [--platform=<platform>] [--provider=<provider>] [--debug]
  molecule list        [--platform=<platform>] [--provider=<provider>] [--debug]
  molecule login <host>
  molecule init  <role>
  molecule -v | --version
  molecule -h | --help

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
   --platform <platform>  specify a platform
   --provider <provider>  specify a provider
   --tags <tag1,tag2>     comma separated list of ansible tags to target
   --debug                get more detail
"""

import sys

from docopt import docopt
from docopt import DocoptExit

import molecule
from provisioners import Ansible


class CLI(object):
    def main(self):
        args = docopt(__doc__)
        if args['--version']:
            print molecule.__version__
            sys.exit(0)

        m = Ansible(args)
        m.main()
        commands = ['create', 'converge', 'idempotence', 'test', 'verify', 'destroy', 'status', 'list', 'login', 'init']
        for command in commands:
            if args[command]:
                try:
                    method = getattr(m, command)
                except AttributeError:
                    raise DocoptExit()

                if callable(method):
                    sys.exit(method())


def main():
    CLI().main()


if __name__ == '__main__':
    main()
