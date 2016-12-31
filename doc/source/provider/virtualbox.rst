Virtualbox
==========

.. code-block:: yaml

  ---
  vagrant:
    platforms:
      - name: ubuntu
        box: ubuntu/trusty32

    providers:
      - name: virtualbox
        type: virtualbox
        options:
          memory: 512

Comprehensive Usage
-------------------

This example is far more extensive than you likely need and it demonstrateslots
of options that you probably don't want to set.

.. code-block:: yaml

  ---
  ansible:
    playbook: playbook.yml
    become: True
    become_user: False
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

    providers:
      - name: virtualbox
        type: virtualbox
        options:
          memory: 512

Other Notes
^^^^^^^^^^^

* `box_version`, defaults to '=', can include an constraints like '<, >, >=,
  <=, ~.' as listed in the `Versioning`_ docs.

.. _`Versioning`: https://docs.vagrantup.com/v2/boxes/versioning.html
