************
Contributing
************

Move to Red Hat
===============

.. important::

    During the end of October 2018 the Molecule Project was moved to its new home
    under Ansible by Red Hat.

Therefore the project is in a state of transition.

There are some implications:

* There is no immediate roadmap but there is a `community working group`_ with
  aspirations to achieve it. Please join the group if you would like to
  influence the direction of the project.

* The coding style currently used (as of early 2019) is not necessarily the
  style that will be followed in future development. Therefore, please
  understand that when reviewers submit several comments relating to style that
  we are in a process of shaping the code base to match the Ansible team
  standards.

.. _community working group: https://github.com/ansible/community/tree/master/group-molecule

Update Git repo location
------------------------

The Molecule project has moved:

old location: ``https://github.com/metacloud/molecule``

new location: ``https://github.com/ansible/molecule``

If you have the source checked out you should use ``git remote set-url origin``
to point to the new location.

Please follow GitHub's official `changing a remote's URL`_ guide.

.. _`changing a remote's URL`: https://help.github.com/articles/changing-a-remote-s-url/

New Docker location
-------------------

For people that use the Docker image, we are now publishing to a new location `Molecule on quay.io`_.

old location: ``https://hub.docker.com/r/retr0h/molecule/``

new location: ``https://quay.io/repository/ansible/molecule``

How to use::

  docker pull quay.io/ansible/molecule:latest

.. _`Molecule on quay.io`: https://quay.io/repository/ansible/molecule


Release announcements
---------------------

Want to know about releases, subscribe to `ansible-announce list`_

.. _`ansible-announce list`: https://groups.google.com/group/ansible-announce

Talk to us
----------

Join us in ``#ansible-molecule`` on `freenode`_, or `molecule-users Forum`_.

The full list of Ansible email lists and IRC channels can be found in the `communication page`_.

.. _`freenode`: https://freenode.net
.. _`molecule-users Forum`: https://groups.google.com/forum/#!forum/molecule-users
.. _`communication page`: https://docs.ansible.com/ansible/latest/community/communication.html

Contribution Guidelines
=======================

* We are interested in various different kinds of improvement for Molecule;
  please feel free to raise an `Issue`_ if you would like to work on something
  major to ensure efficient collaboration and avoid duplicate effort.
* Create a topic branch from where you want to base your work.
* Check for unnecessary whitespace with ``git diff --check`` before committing.
  Please see `formatting`_ and `linting`_ documentation for further commands.
* Make sure you have added tests for your changes.
* You must use ``git commit --signoff`` for any commit to be merged, and agree
  that usage of ``--signoff`` constitutes agreement with the terms of `DCO 1.1`_.

* Run all the tests to ensure nothing else was accidentally broken.
* Reformat the code by following the formatting section below.
* Submit a pull request.

.. _`Issue`: https://github.com/ansible/molecule/issues/new/choose
.. _`DCO 1.1`: https://github.com/ansible/molecule/blob/master/DCO_1_1.md
.. _formatting: https://molecule.readthedocs.io/en/latest/testing.html#formatting
.. _linting: https://molecule.readthedocs.io/en/latest/testing.html#linting

Installing
==========

:ref:`installation` from source or package.

Testing
=======

There is extensive testing built into the `continuous integration`_ of this
project and as a result, the time for successful builds is potentially quite
long (up to and above 1 hour). This depends a lot on the Travis infrastructure
but also on the amount of simultaneous contributions being worked on. Long
build queues can quickly become a very demotivating factor for other
contributors. Until such time that we improve the build speeds we must
therefore ask that you please perform all of the :ref:`full_testing` testing
steps prior to submitting a pull request.

.. _`continuous integration`: https://travis-ci.com/ansible/molecule

Ansible Modules
===============

This project uses the following Ansible modules, and `Gilt`_ to manage them.

- `Ansible Goss`_

To bring in updated upstream modules.  Update `gilt.yml` and execute the following:

.. code-block:: bash

  $ gilt overlay

.. _`Ansible Goss`: https://github.com/indusbox/goss-ansible
.. _`Gilt`: https://gilt.readthedocs.io
