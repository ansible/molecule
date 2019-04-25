#  Copyright (c) 2019 Red Hat, Inc.
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

from molecule.provisioner.lint.ansible_lint import AnsibleLintMixin
from molecule.verifier.lint import base


class AnsibleLint(AnsibleLintMixin, base.Base):
    """
    `Ansible Lint`_ is not the default verifier linter.

    `Ansible Lint`_ checks playbooks for practices, and behaviour that could
    potentially be improved.

    Additional options can be passed to ``ansible-lint`` through the options
    dict. Any option set in this section will override the defaults.

    .. code-block:: yaml

        verifier:
          name: ansible
          lint:
            name: ansible-lint
            options:
              exclude:
                - path/exclude1
                - path/exclude2
              x: ["ANSIBLE0011,ANSIBLE0012"]
              force-color: True

    The ``x`` option must be passed like this due to a `bug`_ in Ansible Lint.

    The role linting can be disabled by setting ``enabled`` to False.

    .. code-block:: yaml

        verifier:
          name: ansible
          lint:
            name: ansible-lint
            enabled: False

    Environment variables can be passed to lint.

    .. code-block:: yaml

        verifier:
          name: ansible
          lint:
            name: ansible-lint
            env:
              FOO: bar

    .. _`Ansible Lint`: https://github.com/ansible/ansible-lint
    .. _`bug`: https://github.com/ansible/ansible-lint/issues/279
    """

    @property
    def _playbook(self):
        return self._config.provisioner.playbooks.verify

    @property
    def _action_env(self):
        return self._config.provisioner.env
