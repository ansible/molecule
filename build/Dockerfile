FROM docker:dind
LABEL maintainer "John Dewey <john@dewey.ws>"

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
"

ENV PIP_PACKAGES="\
    virtualenv \
    molecule \
    ansible \
    docker-py \
"

RUN \
    apk update \
    && apk add --update --no-cache ${PACKAGES} \
    && rm -rf /var/cache/apk/* \
    && pip install --no-cache-dir ${PIP_PACKAGES} \
    && rm -rf /root/.cache \
    && adduser -D -h ${TEST_HOME_DIR} ${TEST_USER} \
    && usermod -aG dockremap ${TEST_USER} \
    && echo "${TEST_USER} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER ${TEST_USER}
ENV SHELL /bin/bash
