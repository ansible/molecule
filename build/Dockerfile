FROM docker:dind
LABEL maintainer "Ansible <info@ansible.com>"

ENV TEST_USER=molecule
ENV TEST_HOME_DIR=/home/${TEST_USER}

ENV PACKAGES="\
    gcc \
    make \
    bash \
    shadow \
    libffi-dev \
    musl-dev \
    openssl-dev \
    py-pip \
    python \
    python-dev \
    linux-headers \
    sudo \
    rsync \
    curl \
    ruby \
    ruby-dev \
    ruby-etc \
    ruby-rdoc \
    ruby-irb \
    git \
    openssh-client \
"

ENV PIP_PACKAGES="\
    molecule[azure,docker,docs,ec2,gce,lxc,openstack,vagrant,windows] \
    virtualenv \
"

ENV GEM_PACKAGES="\
    rubocop \
"

RUN \
    apk update \
    && apk add --update --no-cache ${PACKAGES} \
    && rm -rf /var/cache/apk/* \
    && pip install --upgrade pip \
    && pip install --no-cache-dir ${PIP_PACKAGES} \
    && rm -rf /root/.cache \
    && gem install ${GEM_PACKAGES} \
    && adduser -D -h ${TEST_HOME_DIR} ${TEST_USER} \
    && usermod -aG dockremap ${TEST_USER} \
    && echo "${TEST_USER} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER ${TEST_USER}
ENV SHELL /bin/bash
