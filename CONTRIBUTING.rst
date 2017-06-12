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

.. _`Issue`: https://github.com/metacloud/molecule/issues

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

Perform all of the :ref:`full_testing` testing steps prior to submitting a PR.


Ansible Modules
===============

This project uses the following Ansible modules, and `Gilt`_ to manage them.

- `Ansible Goss`_

To bring in updated upstream modules.  Update `gilt.yml` and execute the following:

.. code-block:: bash

  $ gilt overlay

.. _`Ansible Goss`: https://github.com/indusbox/goss-ansible
.. _`Gilt`: http://gilt.readthedocs.io
