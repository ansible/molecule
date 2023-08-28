# Using Kubevirt

Below you can see a scenario that is using [Kubevirt VMs](https://kubevirt.io/user-guide/) as test hosts. For Ansible to connect with the SSH in the KubeVirt VMs, it will be made accessible through the Service NodePort.
When you run `molecule test --scenario-name kubevirt` the `create`, `converge` and
`destroy` steps will be run one after another.

This example is using Ansible playbooks and it does not need any molecule
plugins to run. You can fully control which test requirements you need to be
installed.

## Prerequisites

The `create.yml` and `destroy.yml` Ansible playbooks require the Ansible collection `kubernetes.core`. For seamless communication with the Kubernetes API server, the collection uses the following environment variables:

- `K8S_AUTH_API_KEY`: This is the token from the service account used to authenticate with the Kubernetes cluster.

- `K8S_AUTH_HOST`: This points to the URL of the Kubernetes cluster's API.

- `K8S_AUTH_VERIFY_SSL`: If set to `false`, this disables the verification of SSL/TLS certificates, which might pose a security risk. It's mainly used for testing environments, particularly when dealing with self-signed certificates.

Additionally, for the playbooks to work, the Kubernetes service account needs specific roles and role bindings to operate in a particular namespace. This ensures the playbook has sufficient privileges to execute commands on the Kubernetes resources. These roles include getting, listing, watching, creating, deleting, and editing virtual machines and services.

```yaml
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: <Molecule Kubernetes Serviceaccount>
  namespace: <Kubernetes VM Namespace>
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: <Kubernetes VM Namespace>
  name: <Molecule Kubernetes Role>
rules:
  - apiGroups: ["kubevirt.io"]
    resources: ["virtualmachines"]
    verbs: ["get", "list", "watch", "create", "delete", "patch", "edit"]
  - apiGroups: [""]
    resources: ["services"]
    verbs: ["get", "list", "watch", "create", "delete", "patch", "edit"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: <Molecule Kubernetes Rolebinding>
  namespace: <Kubernetes VM Namespace>
subjects:
  - kind: ServiceAccount
    name: <Molecule Kubernetes Serviceaccount>
    namespace: <Kubernetes VM Namespace>
roleRef:
  kind: Role
  name: <Molecule Kubernetes Role>
  apiGroup: rbac.authorization.k8s.io
```

You will need to substitute the following placeholders:

- `<Molecule Kubernetes Serviceaccount>`: This refers to the name of the Kubernetes Serviceaccount that the molecule test utilizes to create the KubeVirt VM.
- `<Kubernetes VM Namespace>`: This denotes the name of the Kubernetes namespace where the VMs will be instantiated.
- `<Molecule Kubernetes Role>`: This is the name of the Kubernetes role which encapsulates the necessary permissions for the molecule test to function.
- `<Molecule Kubernetes Rolebinding>`: This represents the name of the Kubernetes rolebinding that associates the role `<Molecule Kubernetes Role>` with the serviceaccount `<Molecule Kubernetes Serviceaccount>`.

## Considerations

- This example is using ephemeral VMs, which enhance the speed of VM creation and cleanup. However, it is important to note that any data in the system will not be retained if the VM is rebooted.
- You don't need to worry about setting up SSH keys. The `create.yml` Ansible playbook takes care of configuring a temporary SSH key.

## Config playbook

```yaml title="molecule.yml"
{!../molecule/kubevirt/molecule.yml!}
```

Please, replace the following parameters:

- `<Kubernetes VM Namespace>`: This should be replaced with the namespace in Kubernetes where you intend to create the KubeVirt VMs.
- `<Kubernetes Node FQDN>`: Change this to the fully qualified domain name (FQDN) of the Kubernetes node that Ansible will attempt to SSH into via the Service NodePort.

```yaml title="requirements.yml"
{!../molecule/kubevirt/requirements.yml!}
```

## Create playbook

```yaml title="create.yml"
{!../molecule/kubevirt/create.yml!}
```

```yaml title="tasks/create_vm.yml"
{!../molecule/kubevirt/tasks/create_vm.yml!}
```

```yaml title="tasks/create_vm_dictionary.yml"
{!../molecule/kubevirt/tasks/create_vm_dictionary.yml!}
```

## Converge playbook

```yaml title="converge.yml"
{!../molecule/kubevirt/converge.yml!}
```

## Destroy playbook

```yaml title="destroy.yml"
{!../molecule/kubevirt/destroy.yml!}
```
