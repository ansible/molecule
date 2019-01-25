*******
LXC driver installation guide
*******

Requirements
============

* LXC

Install
=======

Please refer to the `Virtual environment`_ documentation for installation best
practices. If not using a virtual environment, please consider passing the
widely recommended `'--user' flag`_ when invoking ``pip``.

.. _Virtual environment: https://virtualenv.pypa.io/en/latest/
.. _'--user' flag: https://packaging.python.org/tutorials/installing-packages/#installing-to-the-user-site

.. important::

   Please note, extra system build dependencies may be required for
   ``lxc-python2``, which is the Python dependency required for installing this
   driver. Python 3.X is currently not supported.

.. code-block:: bash

    $ pip install 'molecule[lxc]'

.. important::

    The Ansible LXC modules do not support unprivileged containers. To properly
    use this driver, one must prefix each Molecule command with ``sudo``.
