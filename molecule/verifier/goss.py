#  Copyright (c) 2015-2016 Cisco Systems, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.

import os

from molecule import ansible_playbook
from molecule import util
from molecule.verifier import base

LOG = util.get_logger(__name__)


class Goss(base.Base):
    def __init__(self, molecule):
        super(Goss, self).__init__(molecule)
        self._goss_dir = molecule.config.config['molecule']['goss_dir']
        self._goss_playbook = molecule.config.config['molecule'][
            'goss_playbook']
        self._playbook = self._get_playbook()
        self._ansible = self._get_ansible_instance()

    def execute(self):
        """
        Executes Goss integration tests and returns None.

        :return: None
        """
        if self._get_tests():
            status, output = self._goss()
            if status is not None:
                util.sysexit(status)

    def _goss(self, out=LOG.info, err=LOG.error):
        """
        Executes goss against specified playbook and returns a :func:`sh`
        response object.

        :param out: An optional function to process STDOUT for underlying
         :func:`sh` call.
        :param err: An optional function to process STDERR for underlying
         :func:`sh` call.
        :return: :func:`sh` response object.
        """

        msg = 'Executing goss tests found in {}.'.format(self._playbook)
        util.print_info(msg)

        self._set_library_path()
        return self._ansible.execute()

    def _get_tests(self):
        return os.path.exists(self._playbook)

    def _get_playbook(self):
        return os.path.join(self._goss_dir, self._goss_playbook)

    def _get_ansible_instance(self):
        ac = self._molecule.config.config['ansible']
        ac['playbook'] = self._playbook
        ansible = ansible_playbook.AnsiblePlaybook(
            ac, self._molecule.driver.ansible_connection_params)

        return ansible

    def _set_library_path(self):
        library_path = self._ansible.env.get('ANSIBLE_LIBRARY', '')
        goss_path = self._get_library_path()
        if library_path:
            self._ansible.add_env_arg('ANSIBLE_LIBRARY',
                                      '{}:{}'.format(library_path, goss_path))
        else:
            self._ansible.add_env_arg('ANSIBLE_LIBRARY', goss_path)

    def _get_library_path(self):
        return os.path.join(
            os.path.dirname(__file__), os.path.pardir, os.path.pardir,
            'molecule', 'verifier', 'ansible', 'library')
