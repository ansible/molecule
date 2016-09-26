.. _vagrant_driver_usage:

Example files are created with ``molecule init``.

Usage
-----

This is an example of a set of vagrant instance - for information on specifying
the platform/provider, see :ref:`provider_index`.

.. code-block:: bash

  $ pip install python-vagrant

.. code-block:: yaml

  ---
  instances:
    - name: vagrant-test-01
      ansible_groups:
        - group_1
      interfaces:
        - network_name: private_network
          type: dhcp
          auto_config: true
      options:
        append_platform_to_hostname: no
    - name: vagrant-test-02
      ansible_groups:
        - group_2
      interfaces:
        - network_name: private_network
          type: dhcp
          auto_config: true
      options:
        append_platform_to_hostname: no

Comprehensive Usage
-------------------

.. code-block:: yaml

  ---
  vagrant:
    raw_config_args:
      - "ssh.insert_key = false"
      - "vm.network 'forwarded_port', guest: 80, host: 8080"

    platforms:
      - name: trusty64
        box: trusty64
        box_url: https://vagrantcloud.com/ubuntu/boxes/trusty64/versions/14.04/providers/virtualbox.box

    providers:
      - name: virtualbox
        type: virtualbox
        options:
          memory: 512
          cpus: 2

    instances:
      - name: vagrant-01
        ansible_groups:
          - group_1
          - group_2
          - group_3
          - group_4:children:
            - group_1
            - group_2
        interfaces:
          - network_name: private_network
            type: dhcp
            auto_config: true
          - network_name: private_network
            type: static
            ip: 192.168.0.1
            auto_config: true
        options:
          append_platform_to_hostname: no
        raw_config_args:
          - "vm.network 'private_network', type: 'dhcp', auto_config: false"

A ``box_url`` is not required - if the vagrant box is available on hashicorp,
it can be specified in ``box``. For example, the same image in the previous
example can be invoked like so:

.. code-block:: yaml

  platforms:
    - name: trusty64
      box: ubuntu/trusty64
