#!/bin/sh

set -eux

if command -v apt 1>/dev/null; then
  . /etc/os-release

  apt-get update
  apt-get -y upgrade

  if lsb_release -i | grep -i 'ubuntu'; then
    add-apt-repository ppa:deadsnakes/ppa
    echo "deb https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_${VERSION_ID}/ /" | \
      tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list
    curl -sSL "https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_${VERSION_ID}/Release.key" | \
      tee /etc/apt/trusted.gpg.d/podman.asc

    apt-get update
    apt-get -y upgrade
    apt-get -y install podman python3-pip python3.8 python3.8-distutils \
      python3.9 python3.9-distutils python3.10 python3.10-distutils
  fi

  if lsb_release -i | grep -i 'debian'; then
    apt-get -y install ansible-galaxy build-essential git libbz2-dev \
      libffi-dev libgdbm-dev libncurses5-dev libnss3-dev libreadline-dev \
      libsqlite3-dev libssl-dev podman python3.9 python3-pip wget zlib1g-dev
    wget --no-clobber "https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tgz"
    tar -xf Python-3.10.*.tgz
    cd Python-3.10.*/ || exit 1
    ./configure --enable-optimizations
    make -j "$(nproc)"
    make altinstall
    cd .. || exit 1
  fi
fi

if command -v dnf 1>/dev/null; then
  dnf -y upgrade
  dnf -y install --enablerepo=updates-testing python3.10
  dnf -y install git podman python3-pip python3.10 python3.10-pip
fi

export PATH="/usr/local/bin:${HOME}/.local/bin:$PATH"
pip3 install ansible tox

echo "
  vagrant ssh
  export PATH=\"/usr/local/bin:\${HOME}/.local/bin:\$PATH\"
  cd /vagrant
  time PYTEST_REQPASS=449 tox -e py310-devel
"
