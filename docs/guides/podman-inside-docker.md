# Podman inside Docker

Sometimes your CI system comes prepared to run with Docker but you want
to test podman into it. This `prepare.yml` playbook would let podman run
inside a privileged Docker host by adding some required settings:

```yaml
- name: prepare
  hosts: podman-in-docker
  tasks:
    - name: install fuse-overlayfs
      package:
        name:
          - fuse-overlayfs

    - name: create containers config dir
      file:
        group: root
        mode: a=rX,u+w
        owner: root
        path: /etc/containers
        state: directory

    - name: make podman use fuse-overlayfs storage
      copy:
        content: |
          # See man 5 containers-storage.conf for more information
          [storage]
          driver = "overlay"
          [storage.options.overlay]
          mount_program = "/usr/bin/fuse-overlayfs"
          mountopt = "nodev,metacopy=on"
        dest: /etc/containers/storage.conf
        group: root
        mode: a=r,u+w
        owner: root

    - name: make podman use cgroupfs cgroup manager
      copy:
        content: |
          # See man 5 libpod.conf for more information
          cgroup_manager = "cgroupfs"
        dest: /etc/containers/libpod.conf
        group: root
        mode: a=r,u+w
        owner: root
```

Another option is to configure the same settings directly into the
`molecule.yml` definition:

```yaml
driver:
  name: podman
platforms:
  - name: podman-in-docker
    # ... other options
    cgroup_manager: cgroupfs
    storage_opt: overlay.mount_program=/usr/bin/fuse-overlayfs
    storage_driver: overlay
```

At the time of writing, [Gitlab CI shared runners run privileged Docker
hosts](https://docs.gitlab.com/ee/user/gitlab_com/#shared-runners) and
are suitable for these workarounds.
