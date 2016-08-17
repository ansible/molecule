Usage
-----

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
        port_bindings:
          80: 80
      - name: foo-02
        ansible_groups:
          - group2
        image: ubuntu
        image_version: latest
        registry: testhost:5323
        volume_mounts:
          - '/this/volume:/to/this:rw'
        command: '/bin/sh'
