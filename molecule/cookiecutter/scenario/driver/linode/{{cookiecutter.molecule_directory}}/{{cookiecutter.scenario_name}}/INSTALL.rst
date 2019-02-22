********************************
Linode driver installation guide
********************************

Requirements
============

* ``LINODE_API_KEY`` exposed in your environment

Install
=======

Please refer to the `Virtual environment`_ documentation for installation best
practices. If not using a virtual environment, please consider passing the
widely recommended `'--user' flag`_ when invoking ``pip``.

.. _Virtual environment: https://virtualenv.pypa.io/en/latest/
.. _'--user' flag: https://packaging.python.org/tutorials/installing-packages/#installing-to-the-user-site

.. important:

   Molecule relies on the ``linode-python`` dependency which supports
   Python 2.7+ but is not Python 3.X compatible.

.. code-block:: bash

    $ pip install 'molecule[linode]'
