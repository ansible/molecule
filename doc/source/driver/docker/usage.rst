.. _docker_driver_usage:

Example files are created with ``molecule init --driver docker``.

Usage
-----

.. code-block:: bash

  $ pip install docker-py

.. code-block:: yaml

  ---
  docker:
    containers:
      - name: foo-01
        ansible_groups:
        - group1
        image: ubuntu
        image_version: latest
        privileged: True
        cap_add:
          - SYS_ADMIN
          - MKNOD
        port_bindings:
          80: 80
      - name: foo-02
        ansible_groups:
          - group2
        image: ubuntu
        image_version: '14.04'
        registry: testhost:5323
        volume_mounts:
          - '/this/volume:/to/this:rw'
        links:
          other-container-name: aliased-dns-name
        command: '/bin/sh'

Note: numeric versions need to be put in quotes. If the image version tag is
not a number, it does not need to be in quotes.

A specific registry can also be defined with the ``registry`` option in the
container.  When accessing a private registry, ensure your Docker client is
logged into whichever registry you are trying to access.
