#!/usr/bin/env bash

#  Copyright (c) 2015-2016 Cisco Systems
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

# NOTE(retr0h): A very basic functional test.  Will expand upon this.

set -e

export FUNCTIONAL_TEST_BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export VAGRANT_FUNCTIONAL_TEST_BASE_DIR="${FUNCTIONAL_TEST_BASE_DIR}/vagrant"
export DOCKER_FUNCTIONAL_TEST_BASE_DIR="${FUNCTIONAL_TEST_BASE_DIR}/docker"
ANSIBLE_MAJOR_VERSION=$(ansible --version|head -1|awk '{print $NF}'|cut -d\. -f1)

source ${VIRTUAL_ENV}/bin/activate

echo_info() {
	msg=$1
	cyan=`tput setaf 6`
	reset=`tput sgr0`

	echo "### ${cyan}${msg}${reset}"
}

echo_warn() {
	msg=$1
	yellow=`tput setaf 3`
	reset=`tput sgr0`

	echo "### ${yellow}${msg}${reset}"
}

if [ ${ANSIBLE_MAJOR_VERSION} != 1 ]; then
	echo_info "Docker driver"
	for test in ${DOCKER_FUNCTIONAL_TEST_BASE_DIR}/test_*.bash; do
		echo_info "Testing -> ${test}"
		source ${test}
	done
else
	echo_warn "Docker driver not supported by ansible version -- skipping!"
fi

if [ $(which vagrant) ]; then
	echo_info "Vagrant driver"
	for test in ${VAGRANT_FUNCTIONAL_TEST_BASE_DIR}/test_*.bash; do
		echo_info "Testing -> ${test}"
		source ${test}
	done
else
	echo_warn "Vagrant executable not found -- skipping!"
fi
