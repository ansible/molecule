Usage
-----

All Libvirt specific options(such as the one above, provider specific
and domain options) must be specified in the providers section.  Nevertheless,
other options such as synced or network settings should be added to the
raw_config_args, as they are vagrant generic parameters. Note that you
can use special Libvirt parameters such as "libvirt__tunnel_type", as it
is shown in the example below.

Please, refer to the `vagrant-libvirt`_ documentation for getting a better
understanding of all available options.

.. code-block:: yaml

  ---
  vagrant:
    raw_config_args:
      - "ssh.pty = true"
      - "vm.network :private_network, :libvirt__dhcp_enabled=> false ,:libvirt__tunnel_type => 'server', :libvirt__tunnel_port => '11111'"

    platforms:
      - name: rhel6
        box: rhel/rhel-6
      - name: rhel7
        box: rhel/rhel-7
      - name: centos7
        box: centos/7

    providers:
      - name: libvirt
        type: libvirt
        options:
          memory: 1024
          cpus: 2
          # There are two available drivers: kvm and qemu.
          # Refer to the vagrant-libvirt docs for more info.
          driver: kvm
          video_type: vga

.. _`vagrant-libvirt`: https://github.com/pradels/vagrant-libvirt
