#!/bin/bash
set -euxo pipefail
DIR=$(dirname "$0")
VERSION=$("${DIR}/get-version.sh")

# `-i''` is needed for GNU/BSD sed compatibility
sed -i'' -r "s/^(Version:\s+)[^#]*/\1${VERSION}/"  "${DIR}/molecule.spec"
echo "Version updated to $VERSION in spec file."
