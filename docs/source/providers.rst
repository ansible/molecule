Providers
=========

Vagrant uses `provider plugins`_ to support managing machines on various virtualization platforms. There are workstation-local provider plugins such as `VirtualBox`_ and VMware Fusion/Workstation and cloud-based providers such as OpenStack and AWS/EC2.

Molecule can be configured to give provider-specific configuration data in `molecule.yml` - in the `vagrant.providers` hash. Necessarily, the configuration requirements/options are much more complicated for cloud-based providers than they are for workstation-local virtualization provider plugins.

OpenStack
---------

Molecule is known to work with the `vagrant-openstack-provider`_ provider plugin, which you can install with::

      $ vagrant plugin install vagrant-openstack-provider

.. _`provider plugins`: http://docs.vagrantup.com/v2/providers/index.html
.. _`vagrant-openstack-provider`: https://github.com/ggiamarchi/vagrant-openstack-provider

Commonly, the OpenStack CLI clients are configured using a simple shell script that can be downloaded from Horizon, the OpenStack web interface, `<tenant_name>-openrc.sh`, and which sets a few environment variables to get you going. Molecule makes the assumption that these environment variables are set to get its default behaviour, but these settings can be overridden.

Molecule will generate a Vagrantfile which will default to using these environment variables to set the configuration for `configuration for vagrant-openstack-provider`_:

Credentials
^^^^^^^^^^^

=================================   ======================
vagrant-openstack-provider option   molecule default value
=================================   ======================
openstack_auth_url                  ENV['OS_AUTH_URL']
username                            ENV['OS_USERNAME']
password                            ENV['OS_PASSWORD']
tenant_name                         ENV['OS_TENANT_NAME']
region                              ENV['OS_REGION_NAME']
=================================   ======================

Endpoints
^^^^^^^^^

Different OpenStack distributions often use different endpoints for the various services; if you do not specify any of these to Molecule, vagrant-openstack-provider will try to get them from the catalog endpoint. For completeness, the example shows how to specify them to Molecule so that they get to the provider plugin.

If the defaults are not working for you and you're not sure what to specify, you can discover your OpenStack's endpoints using the command-line clients:

* `nova endpoints` if you are using `python-novaclient`_
* `openstack endpoint list`, followed by `openstack endpoint show <service_type>` if you are using the newer `python-openstackclient`_

Networks
^^^^^^^^

You can specify a list of `Networks`_ which should defined as the YAML description of the data structure described.

Volumes
^^^^^^^

You can specify a list of `Volumes`_ which should defined as the YAML description of the data structure described.
If you want to boot from a volume, instead of an image, specify the volume id in the `volume_boot` key of the provider's platform list.

Stacks
^^^^^^

You can specify a list of `Stacks`_ which should defined as the YAML description of the data structure described.

Simple Example
^^^^^^^^^^^^^^

.. code-block:: yaml

      ---
      ansible:
        playbook: playbook.yml
        sudo: True
        verbose: True

      vagrant:
        raw_config_args:
          - "ssh.insert_key = false"

        platforms:
          - name: ubuntu
            box: ubuntu/trusty32

        providers:
          - name: virtualbox
            type: virtualbox
            options:
              memory: 512
          - name: openstack
            type: openstack
            box: os_dummy
            flavor: m1.small
            platforms:
              - name: ubuntu
                image: ubuntu-14.04-server-cloudimg

Comprehensive Example
^^^^^^^^^^^^^^^^^^^^^

This example is far more extensive than you likely need and it demonstrates lots of options that you probably don't want to set.

.. code-block:: yaml

      ---
      ansible:
        playbook: playbook.yml
        sudo: True
        sudo_user: False
        verbose: True

      vagrant:
        raw_config_args:
          - "ssh.insert_key = false"

        platforms:
          - name: ubuntu
            box: ubuntu/precise32
          - name: trusty64
            box: trusty64
            box_version: "~> 20151130.0.0"
            box_url: https://vagrantcloud.com/ubuntu/boxes/trusty64/versions/14.04/providers/virtualbox.box
          - name: rhel-7
            box: rhel/rhel-7
            triggers:
              - trigger: before
                action: destroy
                cmd: run_remote 'subscription-manager unregister'

        providers:
          - name: virtualbox
            type: virtualbox
            options:
              memory: 512
          - name: openstack
            type: openstack
            username: myname
            password: 'something'
            region: 'RegionOne'
            tenant_name: 'myproject'
            keypair_name: 'mykey'
            private_key_path: "ENV['HOME'] + '/.ssh/id_rsa'"
            box: 'os_dummy'
            flavor: 'm1.small'
            raw_options:
              server_create_timeout: 120
              server_active_timeout: 120
              server_stop_timeout: 60
            endpoints:
              auth_url: 'http://api-cntrl1.os.example.com:5000/v2.0'
              compute_url: 'http://api.cntrl1.mc.metacloud.in:8774/v2'
              image_url: 'http://api-cntrl1.os.example.com:9292/v1'
              network_url: 'http://api-cntrl1.os.example.com:8774/v2'
              volume_url: 'http://api.cntrl1.os.example.com:8776/v1'
            networks:
              - 'mynet1'
              - { name: 'mynet2', address: '192.168.32.3' }
              - { id: 'ab5cc992-95fa-454d-91c1-5d06ed16c2f5', address: '192.168.32.4' }
            security_groups:
              - 'default'
              - 'http'
            platforms:
              - name: ubuntu
                image: 'ubuntu-14.04'
                username: ubuntu
              - name: rhel-7
                volume_boot: '5f580a79-ca75-470e-a956-8b4b3b2ddbb8'
                username: cloud

Other Notes
^^^^^^^^^^^

* `private_key_path`, as with several other values, can be any valid Ruby because it will appear in the Vagrantfile that molecule will generate.

* `box_version`, defaults to '=', can include an constraints like '<, >, >=, <=, ~.' as listed in the `Versioning`_ docs.

* `triggers` enables very basic support for the vagrant-triggers plugin

..  _`configuration for vagrant-openstack-provider`: https://github.com/ggiamarchi/vagrant-openstack-provider/blob/master/README.md#configuration
.. _`VirtualBox`: http://docs.vagrantup.com/v2/virtualbox/index.html
.. _`python-novaclient`: http://pypi.python.org/pypi/python-novaclient
.. _`python-openstackclient`: http://pypi.python.org/pypi/python-openstackclient
.. _`Networks`: https://github.com/ggiamarchi/vagrant-openstack-provider/blob/master/README.md#networks
.. _`Volumes`: https://github.com/ggiamarchi/vagrant-openstack-provider/blob/master/README.md#volumes
.. _`Stacks`: https://github.com/ggiamarchi/vagrant-openstack-provider/blob/master/README.md#orchestration-stacks
.. _`Versioning`: https://docs.vagrantup.com/v2/boxes/versioning.html
