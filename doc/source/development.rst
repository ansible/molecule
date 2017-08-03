***********
Development
***********

* Please read the :ref:`contributing` guidelines.

Branches
========

* The ``master`` branch is stable.  Major changes should be performed
  elsewhere.

Release Engineering
===================

Pre-release
-----------

* Edit the :ref:`changelog`.
* Follow the :ref:`testing` steps.

Release
-------

Molecule follows `Semantic Versioning`_.

.. _`Semantic Versioning`: http://semver.org

Tag the release and push to github.com
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    $ git tag 2.0.0
    $ git push --tags

Upload to `PyPI`_
^^^^^^^^^^^^^^^^^

* Install `Twine`_ using `pip`.

    .. code-block:: bash

        $ pip install twine

* Upload to  `PyPI`_.

    .. code-block:: bash

        $ cd /path/to/molecule
        $ rm -rf build/ dist/
        $ python setup.py sdist bdist_wheel
        $ twine upload dist/*
        $ rm -rf build/ dist/

Post-release
------------

* Comment/close any relevant `Issues`_.
* Announce the release in `#molecule-users`.

Roadmap
=======

* See `Issues`_ on Github.com.

.. _`PyPI`: https://pypi.python.org/pypi/molecule
.. _`ISSUES`: https://github.com/metacloud/molecule/issues
.. _`Twine`: https://pypi.python.org/pypi/twine
