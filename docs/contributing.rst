.. toctree::
   :hidden:

.. _contributing:

************
Contributing
************


* To see what's planned see the `Molecule Project Board`_.
* Join the Molecule `community working group`_ if you would like to
  influence the direction of the project.

.. _community working group: https://github.com/ansible/community/wiki/molecule
.. _Molecule Project Board: https://github.com/ansible-community/molecule/projects


Talk to us
----------

Join us in ``#ansible-molecule`` on `freenode`_, or `molecule-users Forum`_.

The full list of Ansible email lists and IRC channels can be found in the `communication page`_.

.. _`freenode`: https://freenode.net
.. _`molecule-users Forum`: https://groups.google.com/forum/#!forum/molecule-users
.. _`communication page`: https://docs.ansible.com/ansible/latest/community/communication.html

Guidelines
==========

* We are interested in various different kinds of improvement for Molecule;
  please feel free to raise an `Issue`_ if you would like to work on something
  major to ensure efficient collaboration and avoid duplicate effort.
* Create a topic branch from where you want to base your work.
* Check for unnecessary whitespace with ``git diff --check`` before committing.
  Please see `formatting`_ and `linting`_ documentation for further commands.
* Make sure you have added tests for your changes.
* Although not required, it is good to sign off commits using ``git commit --signoff``, and agree
  that usage of ``--signoff`` constitutes agreement with the terms of `DCO 1.1`_.

* Run all the tests to ensure nothing else was accidentally broken.
* Reformat the code by following the formatting section below.
* Submit a pull request.

.. _`Issue`: https://github.com/ansible-community/molecule/issues/new/choose
.. _`DCO 1.1`: https://github.com/ansible-community/molecule/blob/master/DCO_1_1.md
.. _formatting: https://molecule.readthedocs.io/en/latest/testing.html#formatting
.. _linting: https://molecule.readthedocs.io/en/latest/testing.html#linting

Code Of Conduct
===============

Please see our `Code of Conduct`_ document.

.. _Code of Conduct: https://github.com/ansible-community/molecule/blob/master/.github/CODE_OF_CONDUCT.md

Pull Request Life Cycle and Governance
======================================

* If your PRs get stuck `join us on IRC`_ or add to the `working group agenda`_.
* The code style is what is enforced by CI, everything else is off topic.
* All PRs must be reviewed by one other person. This is enforced by GitHub. Larger changes require +2.

.. _working group agenda: https://github.com/ansible/community/wiki/Molecule#meetings
.. _join us on IRC: https://github.com/ansible/community/wiki/Molecule#join-the-discussion

.. _testing:

Testing
=======

Molecule has an extensive set of unit and functional tests.  Molecule uses
`Tox`_ factors to generate a matrix of python x Ansible x unit/functional
tests.  Manual setup required as of this time.

Dependencies
------------

Tests will be skipped when the driver's binary is not present.

Install the test framework `Tox`_.

.. code-block:: bash

    $ python3 -m pip install tox

.. _Tox: https://tox.readthedocs.io/en/latest/
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

Build container images
----------------------

Build the container images with docker or podman.

.. code-block:: bash

    $ tox -e build-containers

Documentation
=============

Working with InterSphinx
------------------------

In the `conf.py`_, we define an ``intersphinx_mapping`` which provides the base
URLs for conveniently linking to other Sphinx documented projects. In order to
find the correct link syntax and text you can link to, you can quickly inspect
the reference from the command line.

For example, if we would like to link to a specific part of the Ansible
documentation, we could first run the following command:

.. code-block:: bash

    python -m sphinx.ext.intersphinx https://docs.ansible.com/ansible/latest/objects.inv

And then see the entire Sphinx listing. We see entries that look like:

.. code-block:: bash

    py:attribute
        AnsibleModule._debug  api/index.html#AnsibleModule._debug

With which we can link out to using the following syntax:

.. code-block:: bash

    :py:attribute:`AnsibleModule._debug`

.. _conf.py: ../source/conf.py


Credits
=======

Based on the good work of John Dewey (`@retr0h`_) and other contributors_.
Active member list can be seen at `Molecule working group`_.

.. _@retr0h: https://github.com/retr0h
.. _contributors: https://github.com/ansible-community/molecule/graphs/contributors
.. _Molecule working group: https://github.com/ansible/community/wiki/Molecule
