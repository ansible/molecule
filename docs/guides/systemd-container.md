## Systemd Container

To start a service which requires systemd, [in a non-privileged
container](https://developers.redhat.com/blog/2016/09/13/running-systemd-in-a-non-privileged-container/),
configure `molecule.yml` with a systemd compliant image, tmpfs, volumes,
and command as follows.

```yaml
platforms:
  - name: instance
    image: quay.io/centos/centos:stream8
    command: /sbin/init
    tmpfs:
      - /run
      - /tmp
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:ro
```

When needed, such security profiles can be reused (for example [the one
available in
Fedora](https://src.fedoraproject.org/rpms/docker/raw/88fa030b904d7af200b150e10ea4a700f759cca4/f/seccomp.json)):

```yaml
platforms:
  - name: instance
    image: debian:stretch
    command: /sbin/init
    security_opts:
      - seccomp=path/to/seccomp.json
    tmpfs:
      - /run
      - /tmp
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:ro
```

The developer can also opt to [start the container with extended
privileges](https://blog.docker.com/2013/09/docker-can-now-run-within-docker/),
by either giving it `SYS_ADMIN` capabilities or running it in
`privileged` mode.

!!! warning

    Use caution when using `privileged` mode or `SYS_ADMIN` capabilities as
    it grants the container elevated access to the underlying system.

To limit the scope of the extended privileges, grant `SYS_ADMIN`
capabilities along with the same image, command, and volumes as shown in
the `non-privileged` example.

```yaml
platforms:
  - name: instance
    image: quay.io/centos/centos:stream8
    command: /sbin/init
    capabilities:
      - SYS_ADMIN
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:ro
```

To start the container in `privileged` mode, set the privileged flag
along with the same image and command as shown in the `non-privileged`
example.

```yaml
platforms:
  - name: instance
    image: quay.io/centos/centos:stream8
    command: /sbin/init
    privileged: True
```
