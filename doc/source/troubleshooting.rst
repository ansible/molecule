.. _troubleshooting:

***************
Troubleshooting
***************

How do I see more debug output?
-------------------------------

You can pass the ``--debug`` flag to Molecule.

You can also configure ``no_log: false`` in the ``molecule.yml``:

.. code-block:: yaml

    provisioner:
      name: ansible
      no_log: false
      lint:
        name: ansible-lint
