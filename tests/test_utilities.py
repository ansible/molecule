#  Copyright (c) 2015 Cisco Systems
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

import testtools

import molecule.utilities as utilities


class TestUtilities(testtools.TestCase):
    def setUp(self):
        super(TestUtilities, self).setUp()

        self.simple_dict_a = {"name": "remy", "city": "Berkeley", "age": 21}
        self.simple_dict_b = {"name": "remy", "city": "Austin"}
        self.deep_dict_a = {"users": {"remy": {"email": "remy@cisco.com", "office": "San Jose", "age": 21}}}
        self.deep_dict_b = {
            "users": {"remy": {"email": "remy@cisco.com",
                               "office": "Austin",
                               "position": "python master"}}
        }

    def test_merge_simple_simple_00(self):
        expected = {"name": "remy", "city": "Austin", "age": 21}
        actual = utilities.merge_dicts(self.simple_dict_a, self.simple_dict_b)
        self.assertEqual(expected, actual)

    def test_merge_simple_simple_01(self):
        expected = {"name": "remy", "city": "Berkeley", "age": 21}
        actual = utilities.merge_dicts(self.simple_dict_b, self.simple_dict_a)
        self.assertEqual(expected, actual)

    def test_merge_simple_deep_00(self):
        expected = {
            "name": "remy",
            "city": "Berkeley",
            "age": 21,
            "users": {"remy": {"email": "remy@cisco.com",
                               "office": "San Jose",
                               "age": 21}}
        }
        actual = utilities.merge_dicts(self.simple_dict_a, self.deep_dict_a)
        self.assertEqual(expected, actual)

    def test_merge_simple_deep_01(self):
        expected = {
            "name": "remy",
            "city": "Berkeley",
            "age": 21,
            "users": {"remy": {"email": "remy@cisco.com",
                               "office": "San Jose",
                               "age": 21}}
        }
        actual = utilities.merge_dicts(self.deep_dict_a, self.simple_dict_a)
        self.assertEqual(expected, actual)

    def test_merge_deep_deep_00(self):
        expected = {
            "users": {"remy": {"age": 21,
                               "email": "remy@cisco.com",
                               "office": "Austin",
                               "position": "python master"}}
        }
        actual = utilities.merge_dicts(self.deep_dict_a, self.deep_dict_b)
        self.assertEqual(expected, actual)

    def test_merge_deep_deep_01(self):
        expected = {
            "users": {"remy": {"age": 21,
                               "email": "remy@cisco.com",
                               "office": "Austin",
                               "position": "python master"}}
        }
        with self.assertRaises(LookupError):
            actual = utilities.merge_dicts(self.deep_dict_a, self.deep_dict_b, raise_conflicts=True)
            self.assertEqual(expected, actual)

    def test_merge_deep_deep_02(self):
        expected = {
            "users":
            {"remy": {"age": 21,
                      "email": "remy@cisco.com",
                      "office": "San Jose",
                      "position": "python master"}}
        }
        actual = utilities.merge_dicts(self.deep_dict_b, self.deep_dict_a)
        self.assertEqual(expected, actual)
