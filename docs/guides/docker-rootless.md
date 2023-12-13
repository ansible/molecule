## Docker With Non-Privileged User

The Molecule Docker driver executes Ansible playbooks as the
root user. If your workflow requires adding support for running as a
non-privileged user, then adapt `molecule.yml` and `Dockerfile.j2` as
follows.

Note: The `Dockerfile` templating and image building processes are only
done for scenarios with `pre_build_image = False`, which is not the
default setting in generated `molecule.yml` files.

To modify the Docker image to support running as a normal user:

Append the following code block to the end of `Dockerfile.j2`. It
creates an `ansible` user with passwordless sudo privileges. Note the
variable `SUDO_GROUP` depends on the target distribution as Debian uses `sudo`
instead of `wheel` group.

```docker
# Create `ansible` user with sudo permissions and membership in `DEPLOY_GROUP`
# This template gets rendered using `loop: "{{ molecule_yml.platforms }}"`, so
# each `item` is an element of platforms list from the molecule.yml file for this scenario.
ENV ANSIBLE_USER=ansible DEPLOY_GROUP=deployer
ENV SUDO_GROUP={{'sudo' if 'debian' in item.image else 'wheel' }}
RUN set -xe \
  && groupadd -r ${ANSIBLE_USER} \
  && groupadd -r ${DEPLOY_GROUP} \
  && useradd -m -g ${ANSIBLE_USER} ${ANSIBLE_USER} \
  && usermod -aG ${SUDO_GROUP} ${ANSIBLE_USER} \
  && usermod -aG ${DEPLOY_GROUP} ${ANSIBLE_USER} \
  && sed -i "/^%${SUDO_GROUP}/s/ALL\$/NOPASSWD:ALL/g" /etc/sudoers
```

Modify `provisioner.inventory` in `molecule.yml` as follows:

```yaml
platforms:
  - name: instance
    image: quay.io/centos/centos:stream8
    # …
```

```yaml
provisioner:
  name: ansible
  # …
  inventory:
    host_vars:
      # setting for the platform instance named 'instance'
      instance:
        ansible_user: ansible
```

Make sure to use your **platform instance name**. In this case
`instance`.

An example for a different platform instance name:

```yaml
platforms:
  - name: centos8
    image: quay.io/centos/centos:stream8
    # …
```

```yaml
provisioner:
  name: ansible
  # …
  inventory:
    host_vars:
      # setting for the platform instance named 'centos8'
      centos8:
        ansible_user: ansible
```

To test it, add the following task to `tasks/main.yml`. It fails,
because the non-privileged user is not allowed to create a folder in
`/opt/`. This needs to be performed using `sudo`.

To perform the task using `sudo`, uncomment `become: yes`. Now the task
will succeed.

```yaml
- name: Create apps dir
  file:
    path: /opt/examples
    owner: ansible
    group: deployer
    mode: 0775
    state: directory
  # become: yes
```

Don't forget to run `molecule destroy` if image has already been
created.
