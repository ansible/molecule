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

List available scenarios
------------------------

List all available scenarios. This is useful to target specific Python and
Ansible version for the functional and unit tests.

    $ tox -l


Unit
----

Run all unit tests with coverage.

.. code-block:: bash

    $ tox -e 'py{27,35,36,37}-ansible{25,26,27}-unit'

Run all unit tests for a specific version of Python and Ansible (here Python 3.7
and Ansible 2.7).

    $ tox -e py37-ansible27-unit

Functional
----------

Run all functional tests for all supported platforms.

.. note::

    The functional tests are a work in progress. They need better structure and
    reuse. They are also very slow and costly in terms of system resources.

.. code-block:: bash

    $ tox -e 'py{27,35,36,37}-ansible{25,26,27}-functional'


Run all functional tests for a specific version of Python and Ansible (here
Python 3.7 and Ansible 2.7).

    $ tox -e py37-ansible27-functional

Run all functional tests targeting the docker driver.

.. code-block:: bash

    $ tox -e 'py{27,35,36,37}-ansible{25,26,27}-functional' -- -v -k docker

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

Check format
^^^^^^^^^^^^

.. code-block:: bash

    $ tox -e format-check

Enforce format
^^^^^^^^^^^^^^

.. code-block:: bash

    $ tox -e format

.. _`YAPF`: https://github.com/google/yapf


Linting
-------

Linting is performed by `Flake8`_.

.. code-block:: bash

    $ tox -e lint

.. _`Flake8`: http://flake8.pycqa.org/en/latest/


Documentation
-------------

Generate the documentation, using `sphinx`_.

.. code-block:: bash

    $ tox -e doc

.. _`sphinx`: http://www.sphinx-doc.org

Metadata validation
-------------------

Check if the long description of the generated package will render properly in
Python eggs and PyPI, using `checkdocs`_ and `twine`_.

.. code-block:: bash

    $ tox -e metadata-validation

.. _`checkdocs`: https://github.com/collective/collective.checkdocs

.. _`twine`: https://twine.readthedocs.io/

Build docker
------------

Build the docker container.

.. code-block:: bash

    $ tox -e build-docker

.. include:: ci.rst
