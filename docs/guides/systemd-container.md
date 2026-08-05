<!-- cspell:ignore oneshot -->
## Systemd Container

To test a role that manages services, the test instance needs `systemd` running as PID 1. The [Using podman containers](../examples/podman.md) example already stands a container up from a plain `create.yml` driven entirely by inventory variables. This guide is the systemd delta on that scenario: you keep its `create.yml`, `destroy.yml`, and `molecule.yml`, point the inventory at init images, and swap converge and verify for playbooks that apply and check a service-managing role.

### Make the instance systemd-capable

The example's `create.yml` already reads `container_image`, `container_command`, and `container_systemd` from inventory, so making the instance systemd-capable is an inventory change, not a change to any playbook. Point each host at an init image, and set the two shared settings as group variables in the same file:

```yaml
# inventory/hosts.yml
all:
  children:
    molecule:
      hosts:
        ubi10:
          container_image: registry.access.redhat.com/ubi10/ubi-init:latest
        centos-stream10:
          container_image: quay.io/centos/centos:stream10
      vars:
        ansible_connection: containers.podman.podman
        container_command: /sbin/init
        container_systemd: always
```

Pick an init image that matches the distribution your role targets. Red Hat's [UBI 10 init image](https://catalog.redhat.com/software/containers/ubi10-init/) ships `systemd` as PID 1 and can be pulled without a subscription; `quay.io/centos/centos:stream10` covers CentOS Stream. The example loops over every host in the `molecule` group, so add as many as you need to test across distributions.

The two shared settings are what turn these into systemd instances:

- `container_command: /sbin/init` runs the image's init as PID 1. The example defaults the command to `sleep 1d`; if you leave that default, `sleep` is PID 1, `systemd` never starts, and converge fails with `System has not been booted with systemd as init system (PID 1)`. Override it to the init.
- `container_systemd: always` puts Podman in systemd mode, wiring up the cgroup and tmpfs mounts `systemd` needs. Use `always` rather than `true`: `true` only auto-detects, and with a command set it will not enable systemd mode.

Running `systemd` as PID 1 needs a cgroup v2 host, which is the default on current distributions; rootless Podman additionally needs the v2 hierarchy delegated to your user.

### Converge and verify

The example's converge and verify inspect the container's OS. Replace them with playbooks that apply your role and check the service it manages.

`converge.yml` applies the role under test. Because the container runs `systemd` as PID 1, a role that installs and manages a service works the same as it would on a full host. `your_role` is whatever role you are testing:

```yaml
# converge.yml
---
- name: Converge
  hosts: molecule
  gather_facts: false
  tasks:
    - name: Apply the role under test
      ansible.builtin.include_role:
        name: your_role
```

`verify.yml` asserts the outcome the guide is about: that `systemd` actually brought the role's unit up. It reads the running services with `service_facts` and fails the scenario if the unit is not active, so a container where `systemd` never took over as PID 1 is caught rather than passing silently. Point the assertion at the unit your role manages; here that unit is `demo.service`:

```yaml
# verify.yml
---
- name: Verify
  hosts: molecule
  gather_facts: false
  tasks:
    - name: Collect the instance's service facts
      ansible.builtin.service_facts:

    - name: Confirm systemd is running the managed service
      ansible.builtin.assert:
        that:
          - "{% raw %}'demo.service' in ansible_facts.services{% endraw %}"
          - "{% raw %}ansible_facts.services['demo.service'].state == 'running'{% endraw %}"
        fail_msg: demo.service is not running
        success_msg: demo.service is active
```

`state == 'running'` is the right check for a long-running unit (`Type=simple` or `exec`). A `Type=oneshot` unit that finished cleanly reports `stopped`, so for those assert on enablement or on the effect the unit produced instead.

### Extended privileges

The example's `create.yml` also reads `container_capabilities` and `container_privileged` from inventory, so extended privileges are inventory changes too, not playbook edits. Most systemd workloads run under the default container above; some need more, for example mounting filesystems or loading kernel modules. Set these on a host, or in the group `vars:` block to apply them to every host:

```yaml
        container_capabilities:
          - SYS_ADMIN
        # or, for full privilege:
        container_privileged: true
```

For a custom seccomp profile, add a `security_opt` field to the example's `create.yml`, which does not expose one by default.

!!! warning

    Use caution with `privileged` mode or `SYS_ADMIN`: they grant the container elevated access to the host. Reach for them only when a specific task needs them, not by default.

### Common failure modes

- **Converge fails with `System has not been booted with systemd as init system (PID 1)`.** The container is running the default `sleep 1d` command instead of the init. Set `container_command` to the image's init (`/sbin/init`) and `container_systemd: always`.
- **The same failure even though you set `container_systemd: always`.** Check where it takes effect. The example ships `group_vars/molecule.yml` with `container_systemd: false`, and a `group_vars` file outranks the group `vars:` set inline in `inventory/hosts.yml`, so the inline value is silently ignored. Remove or update that `group_vars` entry.
- **The service is not running, but the container started.** Confirm the image is an init image (for example `ubi-init`, not plain `ubi`); a plain image has no `systemd` to bring the unit up.
- **The same failure only on an older host.** `systemd` as PID 1 needs cgroup v2. A host still on cgroup v1, or rootless Podman without the v2 hierarchy delegated, brings the container up but never boots `systemd`.
- **`Failed to connect to bus` or other D-Bus errors during converge.** The container answered the connection before `systemd` finished booting. `wait_for_connection` confirms the Podman connection is up, not that `multi-user.target` is reached; if your role needs a completed boot, wait on a unit with `retries`/`until`.
- **Writing into `/etc/systemd/system` fails with permission denied.** The image's default user is not root. Add `become: true` or use an image that runs as root (`ubi-init` does).
