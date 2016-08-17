Usage
-----

This is an example of a set of vagrant instance - for information on specifying
the platform/provider, see :ref:`providers`.

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
