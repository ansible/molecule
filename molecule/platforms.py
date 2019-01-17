#  Copyright (c) 2015-2018 Cisco Systems, Inc.
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

from uuid import uuid4

from molecule import logger


LOG = logger.get_logger(__name__)


def extend_instance_names(config_platforms, unique_id):
    def transformer_func(p):
        p['name'] = '{}-{}'.format(p['name'], unique_id)
        return p
    return [transformer_func(p) for p in config_platforms]


class Platforms(object):
    """
    Platforms define the instances to be tested, and the groups to which the
    instances belong.

    .. code-block:: yaml

        platforms:
          - name: instance-1

    Multiple instances can be provided.

    .. code-block:: yaml

        platforms:
          - name: instance-1
          - name: instance-2

    Mapping instances to groups.  These groups will be used by the Provisioner_
    for orchestration purposes.

    .. code-block:: yaml

        platforms:
          - name: instance-1
            groups:
              - group1
              - group2

    Children allow the creation of groups of groups.

    .. code-block:: yaml

        platforms:
          - name: instance-1
            groups:
              - group1
              - group2
            children:
              - child_group1
    """

    def __init__(self, config):
        """
        Initialize a new platform class and returns None.

        :param config: An instance of a Molecule config.
        :return: None
        """
        self._unique_run_id = str(uuid4())
        config.config['platforms'] = extend_instance_names(
            config.config['platforms'],
            self._unique_run_id,
        )
        self._config = config

    @property
    def instances(self):
        return self._config.config['platforms']
