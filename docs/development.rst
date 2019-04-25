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

* Ensure the `GitHub Project`_ has all cards in the ``Done`` column.
* Edit the :ref:`changelog`, based on the project ``Done`` column.
* Follow the :ref:`testing` steps.

Release
-------

Molecule follows `Semantic Versioning`_.

.. _`Semantic Versioning`: https://semver.org

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

Docker Build
^^^^^^^^^^^^

* `Quay.io`_ automatically builds on commit and tag

.. _`quay.io`: https://quay.io/repository/ansible/molecule

Post-release
------------

* Comment/close any relevant `Issues`_.
* Announce the release in ``#ansible-molecule``.
* Announce on Google Groups: ansible-announce, molecule-users.

Roadmap
=======

* From Molecule v2.20 the `GitHub Project`_ tool is used to track each release.

.. _`PyPI`: https://pypi.org/project/molecule
.. _`GitHub Project`: https://github.com/ansible/molecule/projects
.. _`Issues`: https://github.com/ansible/molecule/issues
