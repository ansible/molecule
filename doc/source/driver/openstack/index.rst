OpenStack
=========

The openstack driver will create instances in your openstack service. The
environment variables required to use this driver can be found in the RC file
provided on your openstack site.

Options
-------

* ``name`` - name of the openstack instance
* ``image`` - openstack image to use for instance
* ``flavor`` - openstack flavor to use for instance
* ``sshuser`` - user to access ssh with
* ``ansible_groups`` - a list of groups the instance(s) belong to in Ansible
  and/or a list of lists for assigning the instance(s) to child groups.
* ``security_groups`` - security groups the instance belongs to in openstack

The ``keypair`` and ``keyfile`` options must also be given to specify the
keypair to use when accessing your openstack service. Usage can be seen in the
example below.
