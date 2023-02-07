# About Ansible Molecule

Molecule project is designed to aid in the development and testing of
[Ansible](https://ansible.com) roles.

Molecule provides support for testing with multiple instances, operating
systems and distributions, virtualization providers, test frameworks and
testing scenarios.

Molecule encourages an approach that results in consistently developed
roles that are well-written, easily understood and maintained.

Molecule supports only the latest two major versions of Ansible (N/N-1),
meaning that if the latest version is 2.9.x, we will also test our code
with 2.8.x.

Once installed, the command line can be called using any of the methods
below:

```bash
molecule ...
python3 -m molecule ...  # python module calling method
```

# External Resources

Below you can see a list of useful articles and presentations, recently
updated being listed first:

- [Ansible Collections: Role Tests with
  Molecule](https://ericsysmin.com/2020/04/30/ansible-collections-role-tests-with-molecule/)
  @ericsysmin
- [Molecule v3 Slides](https://sbarnea.com/slides/molecule/#/)
  @ssbarnea.
- [Testing your Ansible roles with
  Molecule](https://www.jeffgeerling.com/blog/2018/testing-your-ansible-roles-molecule)
  @geerlinguy
- [How to test Ansible and don't go
  nuts](https://www.goncharov.xyz/it/ansible-testing-en.html)
  @ultral
