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

    $ git tag 2.x.x
    $ git push --tags

Upload to `PyPI`_
^^^^^^^^^^^^^^^^^

* Build and upload to  `PyPI`_.

    .. code-block:: bash

        $ make -f build/Makefile build
        $ make -f build/Makefile push
        $ make -f build/Makefile clean

Upload to `Docker Hub`_
^^^^^^^^^^^^^^^^^^^^^^^

* Build and upload to  `Docker Hub`_.

    .. code-block:: bash

        $ make -f build/Makefile docker-build
        $ make -f build/Makefile docker-push

.. _`Docker Hub`: https://hub.docker.com/r/retr0h/molecule/

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
