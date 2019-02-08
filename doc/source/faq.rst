***
FAQ
***

How to skip tasks?
==================

Molecule will skip tasks which are tagged with either ``molecule-notest`` or
``notest``.

Change the test sequence order?
===============================

You can override the ``scenario`` configuration in your ``molecule.yml`` to
specify the test sequence that you would like. Refer to the
:ref:`root_scenario` documentation for more.

How does ``side-effect`` work?
==============================

The optional :ref:`side-effect` playbook executes actions which produce side
effects to the instances. Intended to test HA failover scenarios or the like.
It is not enabled by default. Please see the :ref:`provisioner` documentation
for more.

Can I use Docker in Docker?
===========================

Molecule can be executed via an Alpine Linux container by leveraging ``dind``
(Docker in Docker).  Currently, we only build images for the latest version of
Ansible and Molecule.  In the future we may break this out into Molecule/
Ansible versioned pairs.  The images are located on `quay.io`_.

To test a role, change directory into the role to test, and execute Molecule as
follows.

.. _`quay.io`: https://quay.io/repository/ansible/molecule

.. code-block:: bash

    docker run --rm -it \
        -v "$(pwd)":/tmp/$(basename "${PWD}"):ro \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -w /tmp/$(basename "${PWD}") \
        quay.io/ansible/molecule:latest \
        sudo molecule test

Variable substitution handling?
===============================

.. autoclass:: molecule.interpolation.Interpolator()
   :undoc-members:
