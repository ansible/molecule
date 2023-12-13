## Customizing the Docker Image Used by a Scenario/Platform

The docker driver supports using pre-built images and `docker build`
-ing local customizations for each scenario's platform. The Docker
image used by a scenario is governed by the following configuration
items:

1.  `platforms[*].image`: Docker image name:tag to use as base image.

2.  `platforms[*].pre_build_image`: Whether to customize base image or
    use as-is[^1].

    > - When `true`, use the specified `platform[].image` as-is.
    > - When `false`, exec `docker build` to customize base image
    >   using either:
    >
    >   > - Dockerfile specified by `platforms[*].dockerfile` or
    >   > - Dockerfile rendered from `Dockerfile.j2` template (in
    >   >   scenario dir)

The `Dockerfile.j2` template is generated at
`molecule init scenario`-time when `--driver-name` is `docker`. The
template can be customized as needed to create the desired modifications
to the Docker image used in the scenario.

Note: `platforms[*].pre_build_image` defaults to `true` in each
scenario's generated `molecule.yml` file.

[^1]:
    [Implementation in molecule docker
    driver](https://github.com/ansible-community/molecule-plugins/blob/main/src/molecule_plugins/docker/playbooks/create.yml)
