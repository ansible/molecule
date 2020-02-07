# This is a multi-stage build which requires Docker 17.05 or higher
FROM alpine:edge as molecule-builder

WORKDIR /usr/src/molecule

ENV PACKAGES="\
    gcc \
    git \
    libffi-dev \
    make \
    musl-dev \
    openssl-dev \
    ansible \
    ansible-lint \
    docker-py \
    py3-arrow \
    py3-bcrypt \
    py3-botocore \
    py3-certifi \
    py3-cffi \
    py3-chardet \
    py3-click \
    py3-colorama \
    py3-cryptography \
    py3-docutils \
    py3-flake8 \
    py3-idna \
    py3-jinja2 \
    py3-mccabe \
    py3-netifaces \
    py3-paramiko \
    py3-pbr \
    py3-pexpect \
    py3-pluggy \
    py3-psutil \
    py3-ptyprocess \
    py3-py \
    py3-pycodestyle \
    py3-pynacl \
    py3-pytest \
    py3-requests \
    py3-ruamel \
    py3-setuptools \
    py3-six \
    py3-tabulate \
    py3-urllib3 \
    py3-virtualenv \
    py3-websocket-client \
    python3 \
    python3-dev \
    "
RUN apk add --update --no-cache --repository http://dl-3.alpinelinux.org/alpine/edge/testing/ ${PACKAGES}

ENV MOLECULE_EXTRAS="docker,docs,windows,lint"

# https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=917006
RUN pip3 install -U wheel
ADD . .
RUN \
    pip3 wheel \
    -w dist --no-build-isolation \
    ".[${MOLECULE_EXTRAS}]" testinfra
RUN ls -1 dist/

# ✄---------------------------------------------------------------------
# This is an actual target container:

FROM alpine:edge
LABEL maintainer "Ansible <info@ansible.com>"

ENV PACKAGES="\
    docker \
    git \
    openssh-client \
    ruby \
    ansible \
    ansible-lint \
    docker-py \
    py3-arrow \
    py3-bcrypt \
    py3-botocore \
    py3-certifi \
    py3-cffi \
    py3-chardet \
    py3-click \
    py3-colorama \
    py3-cryptography \
    py3-docutils \
    py3-flake8 \
    py3-idna \
    py3-jinja2 \
    py3-mccabe \
    py3-netifaces \
    py3-paramiko \
    py3-pbr \
    py3-pexpect \
    py3-pluggy \
    py3-psutil \
    py3-ptyprocess \
    py3-py \
    py3-pycodestyle \
    py3-pynacl \
    py3-pytest \
    py3-requests \
    py3-ruamel \
    py3-setuptools \
    py3-six \
    py3-tabulate \
    py3-urllib3 \
    py3-virtualenv \
    py3-websocket-client \
    python3 \
    "

ENV BUILD_DEPS="\
    gcc \
    libc-dev \
    make \
    ruby-dev \
    ruby-rdoc \
    "

ENV PIP_INSTALL_ARGS="\
    --only-binary :all: \
    --no-index \
    -f /usr/src/molecule/dist \
    "

ENV GEM_PACKAGES="\
    rubocop \
    json \
    etc \
    "

ENV MOLECULE_EXTRAS="docker,docs,windows"

RUN \
    apk add --update --no-cache --repository http://dl-3.alpinelinux.org/alpine/edge/testing/ ${BUILD_DEPS} ${PACKAGES} \
    gem install ${GEM_PACKAGES} \
    apk del --no-cache ${BUILD_DEPS} \
    rm -rf /root/.cache
COPY --from=molecule-builder \
    /usr/src/molecule/dist \
    /usr/src/molecule/dist
RUN pip3 install ${PIP_INSTALL_ARGS} "molecule[${MOLECULE_EXTRAS}]"

ENV SHELL /bin/bash
