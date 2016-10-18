************
Contributing
************

* We are interested in various different kinds of improvement for Molecule;
  please feel free to raise an `Issue`_ if you would like to work on something
  major to ensure efficient collaboration and avoid duplicate effort.
* Create a topic branch from where you want to base your work.
* Check for unnecessary whitespace with ``git diff --check`` before committing.
* Make sure you have added tests for your changes.
* Run all the tests to ensure nothing else was accidentally broken.
* Reformat the code by following the formatting section below.
* Submit a pull request.

IRC
===

Join us in the #molecule-users channel on `freenode`_.

.. _`freenode`: https://freenode.net

Installing from source
======================

Due to the rapid pace of development on this tool, you might want to install it
in "`development`_" mode so that new updates can be obtained by simply doing a
``git pull`` in the repository's directory.

.. code-block:: bash

  $ cd /path/to/repos
  $ git clone git@github.com:metacloud/molecule.git
  $ cd molecule
  $ sudo python setup.py develop

There is also a `pip pattern` for development mode:

.. code-block:: bash

  $ cd /path/to/repos
  $ git clone git@github.com:metacloud/molecule.git
  $ pip install -U -e .

.. _`development`: http://pythonhosted.org/setuptools/setuptools.html#development-mode

Testing
=======

Dependencies
------------

Tests will be skipped when the driver's binary is not present. `Serverspec`
scenarios do require a working ruby, `Bunder`_, and `Rake`_.

Install the test framework `Tox`_.

.. code-block:: bash

  $ pip install tox

Install the remaining requirements in a venv (optional):

.. code-block:: bash

  $ pip install -r test-requirements.txt -r requirements.txt

.. _`Bundler`: http://bundler.io
.. _`Rake`: https://github.com/ruby/rake
.. _`Serverspec`: http://serverspec.org

Unit
----

Unit tests are invoked by `Tox`_, and composed of a generative envlist.

.. code-block:: bash

  $ tox -l
  $ py{27}-ansible{19,20,21}-unit

Functional
----------

Functional tests are invoked by `Tox`_, and composed of a generative envlist.

.. code-block:: bash

  $ tox -l
  $ py{27}-ansible{19,20,21}-functional

Formatting
==========

The formatting is done using `YAPF`_.

From the root for the project, run:

.. code-block:: bash

  $ tox -e syntax

.. _`YAPF`: https://github.com/google/yapf
.. _`Tox`: https://tox.readthedocs.io/en/latest
.. _`Issue`: https://github.com/metacloud/molecule/issues
