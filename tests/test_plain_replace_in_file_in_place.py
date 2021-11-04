# The MIT License (MIT)
#
# Copyright (c) 2021 snkas
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import unittest
import exputil
import os


def replace_test(test_obj, input_txt, search_txt, replace_txt, expectation_txt):
    with open("temp.txt", "w+") as f_out:
        f_out.write(input_txt)
    exputil.plain_replace_in_file_in_place("temp.txt", search_txt, replace_txt)
    with open("temp.txt", "r") as f_in:
        test_obj.assertEqual(f_in.read(), expectation_txt)
    os.remove("temp.txt")


class TestPlainReplaceInFileInPlace(unittest.TestCase):

    def test_basic(self):

        # Simple replacement
        replace_test(self, "ABCD", "A", "E", "EBCD")

        # Search term equals replace term
        replace_test(self, "ABABAB", "AB", "AB", "ABABAB")

        # Search term is contained in the replace term
        replace_test(self, "ABABAB", "AB", "ABAB", "ABABABABABAB")

        # Search term is produced as result
        replace_test(self, "BBABAB", "BAB", "", "BAB")

        # Across lines
        replace_test(self, "AB\nAB CD EF\nGH\n\n45", "B\nA", "H", "AHB CD EF\nGH\n\n45")

    def test_failure(self):
        try:
            exputil.plain_replace_in_file_in_place(123456, "ABC", "DEF")
            self.fail()
        except ValueError as e:
            self.assertEqual(str(e), "Target filename must be a str")
        try:
            exputil.plain_replace_in_file_in_place("abcd.txt", 1, "DEF")
            self.fail()
        except ValueError as e:
            self.assertEqual(str(e), "Search text must be a str")
        try:
            exputil.plain_replace_in_file_in_place("abcd.txt", "ABC", 2)
            self.fail()
        except ValueError as e:
            self.assertEqual(str(e), "Replace text must be a str")
        try:
            exputil.plain_replace_in_file_in_place("abcd.txt", "", "DEF")
            self.fail()
        except ValueError as e:
            self.assertEqual(str(e), "Search text cannot be empty")
