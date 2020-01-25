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

.. _full_testing:

Full
----

Run all tests, including linting and coverage reports.  This should be run
prior to merging or submitting a pull request.

.. code-block:: bash

    $ tox

List available scenarios
------------------------

List all available scenarios. This is useful to target specific Python and
Ansible version for the functional and unit tests.

.. code-block:: bash

    $ tox -av

Unit
----

Run all unit tests with coverage.

.. code-block:: bash

    $ tox -e 'py{27,35,36,37,38}-ansible{25,26,27,28}-unit'

Run all unit tests for a specific version of Python and Ansible (here Python 3.7
and Ansible 2.7).

.. code-block:: bash

    $ tox -e py37-ansible28-unit

Linting
-------

Linting is performed by a combination of linters.

Run all the linters (some perform changes to conform the code to the style rules).

.. code-block:: bash

    $ tox -e lint

Documentation
-------------

Generate the documentation, using `sphinx`_.

.. code-block:: bash

    $ tox -e docs

.. _`sphinx`: http://www.sphinx-doc.org

Build docker
------------

Build the docker container.

.. code-block:: bash

    $ tox -e build-docker

.. include:: ci.rst
