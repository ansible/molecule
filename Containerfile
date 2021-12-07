FROM quay.io/packit/packit
LABEL maintainer="Ansible <info@ansible.com>"

# AS packit seems to not install BuildRequires by default:
RUN dnf install -y --setopt=install_weak_deps=False python3-wheel python3-setuptools_scm+toml python3-tox-current-env tox

COPY . /src
CMD /bin/bash
