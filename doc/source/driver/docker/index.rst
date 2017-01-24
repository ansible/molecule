.. _docker_driver_usage:

Docker
======

The Docker driver is compatible with any image that has python installed.
Molecule will automatically install python for images with the appropriate
package tools. A new Docker image will be built with the prefix molecule_local
to separate it from the other images on your system.

The image being used is responsible for implementing the command to execute on
``docker run``.

Below is an example of a ``molecule.yml`` file using two containers `foo-01`
and `foo-02`. `foo-01` is running the latest image of ubuntu and `foo-02`
is running the latest image of ubuntu from a custom registry.

Options
-------

* ``name`` - name of the container.
* ``ansible_groups`` - a list of groups the container(s) belong to in Ansible.
  and/or a list of lists for assigning the container(s) to child groups.
* ``image`` - name of the image.
* ``image_version`` - version of the image.
* ``privileged`` - **(default=False)** whether or not to run the container in
  privileged mode.
* ``registry`` - **(default='')** the registry to obtain the image.
* ``port_bindings`` - **(default={})** the port mapping between the Docker host
  and the container.  This is passed to docker-py as the port_bindings
  `host config`_.
* ``volume_mounts`` - **(default=[])** the volume mappings between the Docker
  host and the container.
* ``cap_add`` - **(default=[])** add Linux Kernel `capability`_ to the Docker
  host.
* ``cap_drop`` - **(default=[])** drop Linux Kernel `capability`_ from the
  Docker host.
* ``command`` - **(default='')** the command to launch the container.
* ``environment`` - **(default=None)** the environment variables passed to the
  container.
* ``links`` - **(default=[])** the link mapping to allow containers to discover
  each other.
* ``network_mode`` - **(default='bridge')** sets the Network mode for the container
- ``bridge'`` - creates a new network stack for the container on the Docker bridge
- ``none`` - no networking for this container
- ``container:[name|id]`` - reuses another containers network stack
- ``host`` -  use the host network stack inside the container or any name that identifies an existing Docker network.

The available param for the Docker driver itself is:

* ``build_image`` - **(default=True)** build an image for use with Molecule.
* ``dockerfile`` - **(default=dockerfile)** supply a custom Dockerfile instead
  of Molecule provided image.

.. _`host config`: https://github.com/docker/docker-py/blob/master/docs/port-bindings.md
.. _`capability`: https://docs.docker.com/engine/reference/run/#/runtime-privilege-and-linux-capabilities
