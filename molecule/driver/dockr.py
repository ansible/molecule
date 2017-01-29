#  Copyright (c) 2015-2017 Cisco Systems, Inc.
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

from molecule.driver import base


class Dockr(base.Base):
    """
    `Docker`_ is the default driver.

    .. code-block:: yaml

        driver:
          name: docker

    .. code-block:: bash

        $ pip install docker-py

    .. _`Docker`: https://www.docker.com
    """

    def __init__(self, config):
        super(Dockr, self).__init__(config)

    @property
    def login_cmd_template(self):
        return 'docker exec -ti {} bash'

    @property
    def safe_files(self):
        return []

    def login_args(self, instance_name):
        return [instance_name]

    def connection_options(self, instance_name):
        return {'ansible_connection': 'docker'}
