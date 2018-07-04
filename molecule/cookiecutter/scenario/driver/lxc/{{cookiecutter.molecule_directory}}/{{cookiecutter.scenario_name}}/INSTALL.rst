*******
Install
*******

Requirements
============

* LXC
* lxc-python2

Install
=======

.. code-block:: bash

    $ sudo pip install lxc-python2

.. important::

    The Ansible LXC modules do not support unprivileged containers.  To properly
    use this driver, one must prefix each Molecule command with `sudo`.
