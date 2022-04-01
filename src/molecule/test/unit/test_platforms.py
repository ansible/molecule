#  Copyright (c) 2015-2018 Cisco Systems, Inc.
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

import pytest

from molecule import platforms


@pytest.fixture
def _instance(config_instance):
    return platforms.Platforms(config_instance)


def test_instances_property(_instance):
    x = [
        {"groups": ["foo", "bar"], "name": "instance-1", "children": ["child1"]},
        {"groups": ["baz", "foo"], "name": "instance-2", "children": ["child2"]},
    ]

    assert x == _instance.instances


@pytest.fixture
def platform_name(request, config_instance):
    return platforms.Platforms(config_instance, platform_name=request.param)


@pytest.mark.parametrize("platform_name", ["instance-1"], indirect=True)
def test_instances_property_with_platform_name_instance_1(platform_name):
    x = [
        {"groups": ["foo", "bar"], "name": "instance-1", "children": ["child1"]},
    ]

    assert x == platform_name.instances


@pytest.mark.parametrize("platform_name", ["instance-2"], indirect=True)
def test_instances_property_with_platform_name_instance_2(platform_name):
    x = [
        {"groups": ["baz", "foo"], "name": "instance-2", "children": ["child2"]},
    ]

    assert x == platform_name.instances
