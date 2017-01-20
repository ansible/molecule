.. _openstack_driver_usage:

OpenStack
=========

The OpenStack driver will create instances in your OpenStack service. The
environment variables required to use this driver can be found in the RC file
provided on your OpenStack site.

Options
-------

* ``name`` - name of the OpenStack instance.
* ``image`` - OpenStack image to use for instance.
* ``flavor`` - OpenStack flavor to use for instance.
* ``sshuser`` - user to ssh as.
* ``ssh_timeout`` - Timeout for checking reachability via ssh in seconds
  (default: ``30``)
* ``ansible_groups`` - a list of groups the instance(s) belong to in Ansible
  and/or a list of lists for assigning the instance(s) to child groups.
* ``security_groups`` - security groups the instance belongs to in OpenStack.
* ``ip_pool`` - Name of the network or floating IP pool to get an
  address from (default: ``None``)
* ``networks``: - Network dict or name or id to attach the server to.

The ``keypair`` and ``keyfile`` options may also be given to specify the
keypair to use when accessing your OpenStack service. If neither ``keypair``
nor ``keyfile`` are specified Molecule will generate a ssh public and private
key and use the public key to create a keypair in your OpenStack service. If
only ``keyfile`` is specified, but no ``keypair``, Molecule will attempt to
locate the public key associated with the ``keyfile`` and use it to generate a
keypair in your OpenStack service. Any dynamic ssh keys or keypairs generated
by Molecule will be deleted on destroy.

The ``ip_pool`` option can be specified at instance or at driver level. If
empty, shade will try to find the right pool by itself.
