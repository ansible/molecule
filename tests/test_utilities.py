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
    def test_deep_merge(self):
        merged_dict_1 = {'test1': 'd1', 'test2': {'test3': 'd1', 'test4': {'test5': 'd1'}}}
        merged_dict_2 = {'test1': 'd2', 'test2': {'test3': 'd1', 'test4': {'test5': 'd2'}, 'test6': 'd2'}}
        merged_dict_final = {'test1': 'd2', 'test2': {'test3': 'd1', 'test4': {'test5': 'd2'}, 'test6': 'd2'}}
        res = utilities.deep_merge(merged_dict_1, merged_dict_2)
        self.assertItemsEqual(res, merged_dict_final)
