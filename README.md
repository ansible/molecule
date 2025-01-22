# About Ansible Molecule

[![PyPI Package](https://img.shields.io/pypi/v/molecule)](https://pypi.org/project/molecule/)
[![Documentation Status](https://readthedocs.org/projects/molecule/badge/?version=latest)](https://ansible.readthedocs.io/projects/molecule)
[![image](https://github.com/ansible-community/molecule/workflows/tox/badge.svg)](https://github.com/ansible-community/molecule/actions)
[![Python Black Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![Ansible Code of Conduct](https://img.shields.io/badge/Code%20of%20Conduct-silver.svg)](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)
[![Discussions](https://img.shields.io/badge/Discussions-silver.svg)](https://forum.ansible.com/tag/molecule)
[![Repository License](https://img.shields.io/badge/license-MIT-brightgreen.svg)](LICENSE)

Molecule project is designed to aid in the development and testing of
[Ansible](https://ansible.com) roles.

Molecule provides support for testing with multiple instances, operating
systems and distributions, virtualization providers, test frameworks and
testing scenarios.

Molecule encourages an approach that results in consistently developed
roles that are well-written, easily understood and maintained.

Molecule supports only the latest two major versions of Ansible (N/N-1).

Once installed, the command line can be called using any of the methods
below:

```bash
molecule ...
python3 -m molecule ...  # python module calling method
```

# Documentation

Read the documentation and more at <https://ansible.readthedocs.io/projects/molecule/>.

# Get Involved

See the [Talk to us](https://ansible.readthedocs.io/projects/molecule/contributing/#talk-to-us) section of the documentation to ask questions, find help, and join the conversation.

For complete details, see the
[Ansible communication guide](https://docs.ansible.com/ansible/devel/community/communication.html).

If you want to get moving fast and make a quick patch:

```bash
$ git clone https://github.com/ansible-community/molecule && cd molecule
$ python3 -m venv .venv && source .venv/bin/activate
$ python3 -m pip install -U setuptools pip tox
```

And you're ready to make your changes!

# Authors

Molecule project was created by [Retr0h](https://github.com/retr0h) and
it is now community-maintained as part of the
[Ansible](https://ansible.com) by Red Hat project.

# License

The
[MIT](https://github.com/ansible-community/molecule/blob/main/LICENSE)
License.

The logo is licensed under the [Creative Commons NoDerivatives 4.0
License](https://creativecommons.org/licenses/by-nd/4.0/).

If you have some other use in mind, contact us.
