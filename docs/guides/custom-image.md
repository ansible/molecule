## Customizing the Docker Image Used by a Scenario/Platform

The docker driver supports using pre-built images and `docker build`
-ing local customizations for each scenario's platform. The Docker
image used by a scenario is governed by the following configuration
items:

1. `platforms[*].image`: Docker image name:tag to use as base image.

2. `platforms[*].pre_build_image`: Whether to customize base image or
    use as-is[^1].

    > - When `true`, use the specified `platform[].image` as-is.
    > - When `false`, exec `docker build` to customize base image
    >   using either:
    >
    >   > - Dockerfile specified by `platforms[*].dockerfile` or
    >   > - Dockerfile rendered from `Dockerfile.j2` template (in
    >   >   scenario dir)

To customize the Docker image, create a `Dockerfile.j2` template file in your scenario directory. Molecule renders this template to build the image for the scenario.

Here is a commonly used example `Dockerfile.j2` that substitutes the base image defined in `molecule.yml` and installs basic dependencies:

{% raw %}

```jinja
# The `item` variable contains the platform configuration from molecule.yml
FROM {{ item.image }}

# Install basic dependencies (example for Debian/Ubuntu based images)
RUN apt-get update && apt-get install -y python3 sudo bash \
    && rm -rf /var/lib/apt/lists/*
```

{% endraw %}

Note: `platforms[*].pre_build_image` defaults to `true` in each
scenario's generated `molecule.yml` file. You must set it to `false` in your platform configuration to instruct Molecule to build the custom image.

[^1]:
    [Implementation in molecule docker
    driver](https://github.com/ansible-community/molecule-plugins/blob/main/src/molecule_plugins/docker/playbooks/create.yml)
