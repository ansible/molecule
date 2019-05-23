**************************************
DigitalOcean driver installation guide
**************************************

Requirements
============

* ``DO_API_KEY`` or ``DO_API_TOKEN`` exposed in your environment
* Only supported on Python 2.7, due to current dependency on dopy

Install
=======

Please refer to the `Virtual environment`_ documentation for installation best
practices. If not using a virtual environment, please consider passing the
widely recommended `'--user' flag`_ when invoking ``pip``.

.. _Virtual environment: https://virtualenv.pypa.io/en/latest/
.. _'--user' flag: https://packaging.python.org/tutorials/installing-packages/#installing-to-the-user-site

.. code-block:: bash

    $ pip install 'molecule[digitalocean]'
