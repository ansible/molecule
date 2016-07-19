Provisioners
============

Molecule uses provisioners to bring up Ansible ready hosts to operate on.
Currently, Molecule supports two provisioners: Vagrant and Docker.

The provisioner can set when using ``init`` command or through the
``molecule.yml`` file.

Docker Provisioner
------------------

The docker provisioner is compatible with any image
that has python installed. Molecule will automatically install
python for images with the yum or apt-get package tools. A new
docker image will be built with the prefix molecule_local to separate it
from the other images on your system.

The image being used is responsible for implementing the command to execute
on ``docker run``.

Below is an example of a ``molecule.yml`` file using two containers ``foo-01`` and
``foo-02``. ``foo-01`` is running the latest image of ubuntu and ``foo-02`` is running
the latest image of ubuntu from a custom registry.

The available params for docker containers are:

* ``name`` - name of the container
* ``ansible_groups`` - groups the container belongs to in Ansible
* ``image`` - name of the image
* ``image_version`` - version of the image
* ``privileged`` - whether or not to run the container in privileged mode (boolean)
* ``registry`` - **(OPTIONAL)** the registry to obtain the image

Docker Example
--------------

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
          - name: foo-02
            ansible_groups:
              - group2
            image: ubuntu
            image_version: latest
            registry: testhost:5323

Vagrant Provisioner
-------------------

The vagrant provisioner performs in a similar manner to the docker provisioner.
Except for using virtual machines instead of containers. Each instance of a vagrantbox
are defined inside of an instance with similar options to docker. The provisioner is
set to vagrant by default if the ``--docker`` flag is not passed when ``molecule init`` is run.

The available parameters for vagrant instances are:

* ``name`` - name of the vagrant box
* ``ansible_groups`` - groups the instance belongs to in ansible
* ``interfaces`` - network inferfaces (see ``usage``)
* ``options`` - Vagrant options supported by Molecule
* ``raw_config_args`` - Vagrant options unsupported by Molecule

Vagrant Instance Example
------------------------

This is an example of a set of vagrant instance - for information on specifying the platform/
provider, see :ref:`providers`.

.. code-block:: yaml

    ---
    instances:
      - name: vagrant-test-01
        ansible_groups:
          - group_1
        interfaces:
          - network_name: private_network
            type: dhcp
            auto_config: true
        options:
          append_platform_to_hostname: no
      - name: vagrant-test-02
        ansible_groups:
          - group_2
        interfaces:
          - network_name: private_network
            type: dhcp
            auto_config: true
        options:
          append_platform_to_hostname: no

Openstack Provisioner
---------------------

The openstack provisioner will create instances in your openstack service. The environment variables required
to use this provisioner can be found in the RC file provided on your openstack site.

The available parameters for openstack instances are:

* ``name`` - name of the openstack instance
* ``image`` - openstack image to use for instance
* ``flavor`` - openstack flavor to use for instance
* ``sshuser`` - user to access ssh with
* ``ansible_groups`` - groups the instance belongs to in ansible
* ``security_groups`` - security groups the instance belongs to in openstack

The ``keypair`` and ``keyfile`` options must also be given to specify the keypair to use when accessing your openstack
service. Usage can be seen in th example below.


Openstack instance example
--------------------------

.. code-block:: yaml

    ---
    openstack:
      keypair: KeyName
      keyfile: ~/.ssh/id_rsa
      instances:
        - name: my_instance
          image: 'CentOS 7'
          flavor: m1.xlarge
          sshuser: centos
          ansible_groups:
            - ansiblegroup


Implementing Provisioners
-------------------------


