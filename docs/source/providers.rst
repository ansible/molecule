.. _providers:

Providers
=========

Vagrant uses `provider plugins`_ to support managing machines on various virtualization platforms. There are workstation-local provider plugins such as `VirtualBox`_ and VMware Fusion/Workstation and cloud-based providers such as AWS/EC2.

Molecule can be configured to give provider-specific configuration data in `molecule.yml` - in the `vagrant.providers` hash. Necessarily, the configuration requirements/options are much more complicated for cloud-based providers than they are for workstation-local virtualization provider plugins.

Simple Example
^^^^^^^^^^^^^^

.. code-block:: yaml

      ---
      ansible:
        playbook: playbook.yml
        sudo: True
        verbose: vvvv

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

Comprehensive Example
^^^^^^^^^^^^^^^^^^^^^

This example is far more extensive than you likely need and it demonstrates lots of options that you probably don't want to set.

.. code-block:: yaml

      ---
      ansible:
        playbook: playbook.yml
        sudo: True
        sudo_user: False
        verbose: vvvv

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

Other Notes
^^^^^^^^^^^

* `box_version`, defaults to '=', can include an constraints like '<, >, >=, <=, ~.' as listed in the `Versioning`_ docs.

* `triggers` enables very basic support for the vagrant-triggers plugin. During `molecule create`, if the plugin is not found it will be automatically installed.

.. _`VirtualBox`: http://docs.vagrantup.com/v2/virtualbox/index.html
.. _`Versioning`: https://docs.vagrantup.com/v2/boxes/versioning.html
.. _`provider plugins`: https://www.vagrantup.com/docs/providers/
