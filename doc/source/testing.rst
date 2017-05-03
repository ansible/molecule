Testing
=======

Molecule has an extensive set of unit and functional tests.  Molecule uses
`Tox`_ `Factors`_ to generate a matrix of python x Ansible x unit/functional
tests.  Manual setup required as of this time.

.. _`Tox`: https://tox.readthedocs.io/en/latest
.. _`Factors`: https://tox.readthedocs.io/en/latest/config.html#factors-and-factor-conditional-settings

Full
^^^^

Boot static instances prior to running the tests.

.. code-block:: bash

    $ docker run \
        -d \
        --name static-instance-docker \
        --hostname static-instance-docker \
        -it molecule_local/ubuntu:latest sleep infinity & wait

    $ vagrant up
    $ vagrant ssh-config > /tmp/ssh-config

Run all tests, including linting and coverage reports.  This should be run
prior to merging or submitting a pull request.

.. code-block:: bash

    $ tox

Unit
^^^^

Run all unit tests with coverage.

.. code-block:: bash

    $ tox -e $(tox -l | grep unit | paste -d, -s -)


Functional
^^^^^^^^^^

Run all functional tests.

.. note::

    The functional tests are a work in progress.  They need better structure
    and reuse.

.. code-block:: bash

    $ tox -e $(tox -l | grep functional | paste -d, -s -)

LXC
^^^

Follow the steps detailed in the Vagrantfile below.

.. code-block:: bash

    $ cd test/functional/lxc
    $ vagrant up

LXD
^^^

Follow the steps detailed in the Vagrantfile below.

.. code-block:: bash

    $ cd test/functional/lxd
    $ vagrant up
