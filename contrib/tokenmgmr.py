#! /usr/bin/env python

#  Copyright (c) 2019 Red Hat, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.

"""CLI tool to retrieve driver provider tokens for CI testing.

This module provides an interface to conveniently retrieve tokens that are used
to provision molecule instances from driver providers for the purpose of
functional testing.

This tool should only be invoked during the CI run (Travis, currently) due to
the fact that the tool requires CI environment variables that are only
accessible through the CI configuration.

Please note, because this script is used before any dependencies of the project
are installed, we must only use a Python implementation that relies on the
standard library.
"""

import argparse
import json
import os
import shlex
import subprocess
import sys


def _ensure_hetzner_cloud_tts_token():
    """Check that a Hetzner Cloud TTS token is exposed."""
    tts_token = os.getenv('HETZNER_CLOUD_TTS_TOKEN')

    if not tts_token or tts_token == '':
        sys.exit(
            (
                'No Hetzner Cloud TTS token available. Please '
                'refer to the CI service configuration which should '
                'be configured to expose this environment variable.'
            )
        )


def _ensure_hetzner_cloud_api_token():
    """Check that a Hetzner Cloud API token is exposed."""
    api_token = os.getenv('HCLOUD_TOKEN')

    if not api_token or api_token == '':
        sys.exit('No Hetzner Cloud API token environment variable exposed')


def _get_hetzner_cloud_token():
    """Retrieve a Hetzner Cloud API token."""
    _ensure_hetzner_cloud_tts_token()

    tts_token = os.getenv('HETZNER_CLOUD_TTS_TOKEN')

    cmd = shlex.split(
        (
            'curl '
            '-X POST '
            '-A travis-ansible-provider '
            '-H "Authorization: Bearer {}" '
            'https://tt-service.hetzner.cloud/token'
        ).format(tts_token)
    )

    EXPECTED_TOKEN_LENGTH = 64

    try:
        payload = subprocess.check_output(cmd).strip()
        loaded = json.loads(payload)
        assert len(loaded['token']) == EXPECTED_TOKEN_LENGTH  # sanity checking
        return loaded['token']
    except subprocess.CalledProcessError as exception:
        sys.exit(
            (
                'Unable to retrieve Hetzner Cloud API token '
                'via a curl invocation. Saw the following '
                'error: {}'
            ).format(str(exception))
        )
    except KeyError:
        sys.exit('Expecting "token" key in response payload')
    except (TypeError, json.decoded.JSONDecodeError) as exception:
        sys.exit('Unable to load JSON. Saw: {}'.format(str(exception)))
    except AssertionError as exception:
        sys.exit(str(exception))


def _remove_hetzner_cloud_token():
    """Remove a Hetzner Cloud API token."""
    _ensure_hetzner_cloud_tts_token()
    _ensure_hetzner_cloud_api_token()

    api_token = os.getenv('HCLOUD_TOKEN')
    tts_token = os.getenv('HETZNER_CLOUD_TTS_TOKEN')

    cmd = shlex.split(
        (
            'curl '
            '-X DELETE '
            '-A travis-ansible-provider '
            '-H "Authorization: Bearer {}" '
            'https://tt-service.hetzner.cloud/token?token={}'
        ).format(tts_token, api_token)
    )

    try:
        return subprocess.check_output(cmd).strip()
    except subprocess.CalledProcessError as exception:
        sys.exit(
            (
                'Unable to remove a Hetzner Cloud API token '
                'via a curl invocation. Saw the following '
                'error: {}'
            ).format(str(exception))
        )


def build_parser():
    """Construct an argument parser."""
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest='command')

    parser_get = subparsers.add_parser('get', help='Retrieve CI token')
    parser_get.add_argument(
        '-d',
        '--driver',
        choices=['hetznercloud'],
        required=True,
        help='Name of driver to get token for',
    )

    parser_remove = subparsers.add_parser('remove', help='Remove CI token')
    parser_remove.add_argument(
        '-d',
        '--driver',
        choices=['hetznercloud'],
        required=True,
        help='Name of driver to remove token for',
    )

    return parser


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()

    if args.command == 'get':
        if args.driver == 'hetznercloud':
            print(_get_hetzner_cloud_token())
    elif args.command == 'remove':
        if args.driver == 'hetznercloud':
            print(_remove_hetzner_cloud_token())
    else:
        parser.print_help()
