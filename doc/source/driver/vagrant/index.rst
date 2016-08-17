Vagrant
=======

The vagrant driver performs in a similar manner to the docker driver.  Except
for using virtual machines instead of containers. Each instance of a vagrantbox
are defined inside of an instance with similar options to docker. The driver is
set to vagrant by default if the ``--docker`` flag is not passed when
``molecule init`` is run.

Options
-------

* ``name`` - name of the vagrant box
* ``ansible_groups`` - groups the instance belongs to in ansible
* ``interfaces`` - network inferfaces (see ``usage``)
* ``options`` - Vagrant options supported by Molecule
* ``raw_config_args`` - Vagrant options unsupported by Molecule
