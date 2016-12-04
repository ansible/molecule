Vagrant
=======

The vagrant driver performs in a similar manner to the Docker driver.  Except
for using virtual machines instead of containers. Each instance of a vagrantbox
are defined inside of an instance with similar options to Docker. The driver is
set to vagrant by default if the ``--docker`` flag is not passed when
``molecule init`` is run.

Options
-------

* ``name`` - name of the vagrant box
* ``ansible_groups`` - a list of groups the instance(s) belong to in Ansible
  and/or a list of lists for assigning the instance(s) to child groups.
* ``interfaces`` - network inferfaces (see ``usage``)
* ``options`` - Vagrant options supported by Molecule
* ``raw_config_args`` - Vagrant options unsupported by Molecule
