Parallels
=========

.. code-block:: yaml

  ---
  vagrant:
    platforms:
      - name: ubuntu
        box: ubuntu/trusty32

    providers:
      - name: parallels
        type: parallels
        options:
          memory: 512
