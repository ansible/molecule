.. _openstack_driver_usage:

Example files are created with ``molecule init --driver openstack``.

Usage
-----

.. code-block:: bash

  $ pip install shade

.. code-block:: yaml

  ---
  openstack:
    keypair: KeyName
    keyfile: ~/.ssh/id_rsa
    instances:
      - name: my_instance
        image: 'CentOS 7'
        flavor: m1.xlarge
        sshuser: centos
        ansible_groups:
          - ansiblegroup
