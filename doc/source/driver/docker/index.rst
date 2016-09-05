Docker
======

The docker driver is compatible with any image that has python installed.
Molecule will automatically install python for images with the yum or apt-get
package tools. A new docker image will be built with the prefix molecule_local
to separate it from the other images on your system.

The image being used is responsible for implementing the command to execute on
``docker run``.

Below is an example of a ``molecule.yml`` file using two containers ``foo-01``
and ``foo-02``. ``foo-01`` is running the latest image of ubuntu and ``foo-02``
is running the latest image of ubuntu from a custom registry.

Options
-------

* ``name`` - name of the container
* ``ansible_groups`` - groups the container belongs to in Ansible
* ``image`` - name of the image
* ``image_version`` - version of the image
* ``privileged`` - **(OPTIONAL)** whether or not to run the container in
  privileged mode (boolean)
* ``registry`` - **(OPTIONAL)** the registry to obtain the image
* ``install_python`` - **(default=yes)** install python onto the image being
  used
* ``port_bindings`` - **(OPTIONAL)** the port mapping between the Docker host
  and the container.  This is passed to docker-py as the port_bindings
  `host config`_.
* ``volume_mounts`` - **(OPTIONAL)** the volume mappings between the Docker
  host and the container.
* ``command`` - **(OPTIONAL)** the command to launch the container with

The available param for the docker driver itself is:

* ``build_image`` - **(default=yes)** build image with python support or use custom dockerfile
* ``dockerfile`` - **dockerfile** to use when building. By default the dockerfile will just install python onto the image given.

.. _`host config`: https://github.com/docker/docker-py/blob/master/docs/port-bindings.md
