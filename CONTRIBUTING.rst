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

Installing
==========

:ref:`installing` from source or package.

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
