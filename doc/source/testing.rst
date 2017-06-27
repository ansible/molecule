.. _testing:

Testing
=======

Molecule has an extensive set of unit and functional tests.  Molecule uses
`Tox`_ `Factors`_ to generate a matrix of python x Ansible x unit/functional
tests.  Manual setup required as of this time.

Dependencies
------------

Tests will be skipped when the driver's binary is not present.

Install the test framework `Tox`_.

.. code-block:: bash

    $ pip install tox

Install `tox-tags`_.

.. _`tox-tags`: https://github.com/AndreLouisCaron/tox-tags

Install the remaining requirements in a venv (optional).

.. code-block:: bash

    $ pip install -r test-requirements.txt -r requirements.txt

.. _`Tox`: https://tox.readthedocs.io/en/latest

.. _full_testing:

Full
----

Run all tests, including linting and coverage reports.  This should be run
prior to merging or submitting a pull request.

.. code-block:: bash

    $ tox

Unit
----

Run all unit tests with coverage.

.. code-block:: bash

    $ tox -t unit

Functional
----------

Run all functional tests.

.. note::

    The functional tests are a work in progress.  They need better structure
    and reuse.

.. code-block:: bash

    $ tox -t functional

Run all functional tests targeting the docker driver.

.. code-block:: bash

    $ tox -t functional -- -v -k docker

Static
^^^^^^

Run all the functional static tests.

.. code-block:: bash

    $ ansible-playbook -i test/resources/playbooks/static/inventory \
      test/resources/playbooks/static/create.yml
    $ tox -t functional -- --static -v -k static
    $ ansible-playbook -i test/resources/playbooks/static/inventory \
      test/resources/playbooks/static/destroy.yml

Formatting
----------

The formatting is done using `YAPF`_.

.. code-block:: bash

    $ tox -e format

.. _`YAPF`: https://github.com/google/yapf


Linting
-------

Linting is performed by `Flake8`_.

.. code-block:: bash

    $ tox -e $(tox -l | grep lint | paste -d, -s -)

.. _`Flake8`: http://flake8.pycqa.org/en/latest/

LXC
---

Follow the steps detailed in the Vagrantfile below.

.. code-block:: bash

    $ cd test/functional/lxc
    $ vagrant up

LXD
---

Follow the steps detailed in the Vagrantfile below.

.. code-block:: bash

    $ cd test/functional/lxd
    $ vagrant up

.. include:: ci.rst
