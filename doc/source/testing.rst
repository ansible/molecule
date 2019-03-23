.. _testing:

Testing
=======

Molecule has an extensive set of unit and functional tests.  Molecule uses
`Tox`_ `Factors`_ to generate a matrix of python x Ansible x unit/functional
tests.  Manual setup required as of this time.

Dependencies
------------

Tests will be skipped when the driver's binary is not present.

Install the test framework `Tox`_ and remaining test requirements.

.. code-block:: bash

    $ pip install tox
    $ pip install -r test-requirements.txt

For some tests `RuboCop`_ is required.

.. code-block:: bash

    # apt-get install ruby ruby-dev
    # gem install rubocop

.. _`RuboCop`: http://batsov.com/rubocop/

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

Delegated
^^^^^^^^^

Run all the functional delegated tests.

.. code-block:: bash

    $ ansible-playbook -i test/resources/playbooks/delegated/inventory \
      test/resources/playbooks/delegated/create.yml
    $ tox -t functional -- --delegated -v -k delegated
    $ ansible-playbook -i test/resources/playbooks/delegated/inventory \
      test/resources/playbooks/delegated/destroy.yml

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

.. include:: ci.rst
