VMware Fusion
=============

.. code-block:: yaml

  ---
  vagrant:
    platforms:
      - name: ubuntu
        box: ubuntu/trusty32

    providers:
      - name: vmware_fusion
        type: vmware_fusion
        options:
          memory: 512
