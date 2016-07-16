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

import binascii
import os

import pytest
import molecule.utilities as utilities


@pytest.fixture()
def simple_dict_a():
    return {"name": "remy", "city": "Berkeley", "age": 21}


@pytest.fixture()
def simple_dict_b():
    return {"name": "remy", "city": "Austin"}


@pytest.fixture()
def deep_dict_a():
    return {"users": {"remy": {"email": "remy@cisco.com",
                               "office": "San Jose",
                               "age": 21}}}


@pytest.fixture()
def deep_dict_b():
    return {
        "users": {"remy": {"email": "remy@cisco.com",
                           "office": "Austin",
                           "position": "python master"}}
    }


def test_merge_simple_simple_00(simple_dict_a, simple_dict_b):
    expected = {"name": "remy", "city": "Austin", "age": 21}
    actual = utilities.merge_dicts(simple_dict_a, simple_dict_b)

    expected == actual


def test_merge_simple_simple_01(simple_dict_b, simple_dict_a):
    expected = {"name": "remy", "city": "Berkeley", "age": 21}
    actual = utilities.merge_dicts(simple_dict_b, simple_dict_a)

    assert expected == actual


def test_merge_simple_deep_00(simple_dict_a, deep_dict_a):
    expected = {
        "name": "remy",
        "city": "Berkeley",
        "age": 21,
        "users": {"remy": {"email": "remy@cisco.com",
                           "office": "San Jose",
                           "age": 21}}
    }
    actual = utilities.merge_dicts(simple_dict_a, deep_dict_a)

    assert expected == actual


def test_merge_simple_deep_01(deep_dict_a, simple_dict_a):
    expected = {
        "name": "remy",
        "city": "Berkeley",
        "age": 21,
        "users": {"remy": {"email": "remy@cisco.com",
                           "office": "San Jose",
                           "age": 21}}
    }
    actual = utilities.merge_dicts(deep_dict_a, simple_dict_a)

    assert expected == actual


def test_merge_deep_deep_00(deep_dict_a, deep_dict_b):
    expected = {
        "users": {"remy": {"age": 21,
                           "email": "remy@cisco.com",
                           "office": "Austin",
                           "position": "python master"}}
    }
    actual = utilities.merge_dicts(deep_dict_a, deep_dict_b)

    assert expected == actual


def test_merge_deep_deep_01(deep_dict_a, deep_dict_b):
    expected = {
        "users": {"remy": {"age": 21,
                           "email": "remy@cisco.com",
                           "office": "Austin",
                           "position": "python master"}}
    }
    with pytest.raises(LookupError):
        actual = utilities.merge_dicts(deep_dict_a,
                                       deep_dict_b,
                                       raise_conflicts=True)
        assert expected == actual


def test_merge_deep_deep_02(deep_dict_b, deep_dict_a):
    expected = {
        "users": {"remy": {"age": 21,
                           "email": "remy@cisco.com",
                           "office": "San Jose",
                           "position": "python master"}}
    }
    actual = utilities.merge_dicts(deep_dict_b, deep_dict_a)

    assert expected == actual


# TODO(retr0h): Cleanup how we deal with temp files
def test_write_template():
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'support')
    src = os.path.join(d, 'test_write_template.j2')
    tmp_file = '/tmp/test_utilities_write_template.tmp'
    utilities.write_template(src, tmp_file, {'test': 'chicken'})
    with open(tmp_file, 'r') as f:
        data = f.read()
    os.remove(tmp_file)

    assert data == 'this is a chicken\n'


# TODO(retr0h): Cleanup how we deal with temp files
def test_write_file():
    tmp_file = '/tmp/test_utilities_write_file.tmp'
    contents = binascii.b2a_hex(os.urandom(15))
    utilities.write_file(tmp_file, contents)
    with open(tmp_file, 'r') as f:
        data = f.read()
    os.remove(tmp_file)

    assert data == contents


def test_format_instance_name_00():
    instances = [{'name': 'test-01'}]
    actual = utilities.format_instance_name('test-02', 'rhel-7', instances)

    assert actual is None


def test_format_instance_name_01():
    instances = [{'name': 'test-01'}]
    actual = utilities.format_instance_name('test-01', 'rhel-7', instances)

    assert 'test-01' == actual


def test_format_instance_name_02():
    instances = [{'name': 'test-01',
                  'options': {'append_platform_to_hostname': True}}]
    actual = utilities.format_instance_name('test-01', 'rhel-7', instances)

    assert 'test-01-rhel-7' == actual


def test_format_instance_name_03():
    instances = [{'name': 'test-01', 'options': {'chicken': False}}]
    actual = utilities.format_instance_name('test-01', 'rhel-7', instances)

    assert 'test-01' == actual


def test_remove_args():
    test_list = ['tags', 'molecule1', 'platform', 'ubuntu', 'tags',
                 'molecule2']
    test_dict = {'tags': 'molecule1', 'platform': 'ubuntu'}
    expected_list = ['platform', 'ubuntu']
    expected_dict = {'platform': 'ubuntu'}
    actual_list, actual_dict = utilities.remove_args(test_list, test_dict,
                                                     ['tags'])

    assert expected_list == actual_list
    assert expected_dict == actual_dict
