# Copyright 2019 snkas
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from exputil import *


class TestProperties(unittest.TestCase):

    def test_positive(self):
        local_shell = LocalShell()
        local_shell.make_full_dir("temp")
        local_shell.write_file("temp/test.txt", "a=5\nb=9.8\nc=abc\nr=-4\nabc = -999.2\nfff =  \"r\"\ngg= \"\n"
                                                "xy =\"\"\nmm=0.0\nnn=1.0\nuu=0.99999")
        config = PropertiesConfig("temp/test.txt")
        self.assertEqual(config.get_property_or_fail("a"), "5")
        self.assertEqual(parse_positive_int(config.get_property_or_fail("a")), 5)
        self.assertEqual(config.get_property_or_default("d", "l"), "l")
        self.assertEqual(config.get_property_or_default("c", "l"), "abc")
        self.assertEqual(config.get_property_or_default("c", "l"), "abc")
        self.assertEqual(config.get_property_or_fail("fff"), "r")
        self.assertEqual(config.get_property_or_fail("gg"), "\"")
        self.assertEqual(config.get_property_or_fail("xy"), "")
        self.assertEqual(parse_positive_float(config.get_property_or_fail("b")), 9.8)
        self.assertEqual(parse_positive_int_less_than(config.get_property_or_fail("a"), 6), 5)
        self.assertEqual(parse_float_between_0_and_1(config.get_property_or_fail("mm")), 0.0)
        self.assertEqual(parse_float_between_0_and_1(config.get_property_or_fail("nn")), 1.0)
        self.assertEqual(parse_float_between_0_and_1(config.get_property_or_fail("uu")), 0.99999)

    def test_negative(self):
        local_shell = LocalShell()
        local_shell.make_full_dir("temp")
        local_shell.write_file("temp/test.txt", "a=5\nb=9.8\nc=abc\nr=-4\nabc=-999.2\nx=-0.00001")
        config = PropertiesConfig("temp/test.txt")

        # Key does not exist
        try:
            config.get_property_or_fail("test")
            self.fail()
        except ValueError:
            self.assertTrue(True)

        # Not a string when parsing
        try:
            parse_positive_float(5.6)
            self.fail()
        except ValueError:
            self.assertTrue(True)

        # Negative float
        try:
            parse_positive_float(config.get_property_or_fail("abc"))
            self.fail()
        except ValueError:
            self.assertTrue(True)

        # Not a float
        try:
            parse_positive_float(config.get_property_or_fail("c"))
            self.fail()
        except ValueError:
            self.assertTrue(True)

        # Negative int
        try:
            parse_positive_int(config.get_property_or_fail("r"))
            self.fail()
        except ValueError:
            self.assertTrue(True)

        # Not an int
        try:
            parse_positive_int(config.get_property_or_fail("abc"))
            self.fail()
        except ValueError:
            self.assertTrue(True)

        # Not below (1)
        try:
            parse_positive_int_less_than(config.get_property_or_fail("a"), 5)
            self.fail()
        except ValueError:
            self.assertTrue(True)

        # Not below (2)
        try:
            parse_positive_int_less_than(config.get_property_or_fail("a"), 0)
            self.fail()
        except ValueError:
            self.assertTrue(True)

        # Not between 0 and 1 (1)
        try:
            parse_float_between_0_and_1(config.get_property_or_fail("b"))
            self.fail()
        except ValueError:
            self.assertTrue(True)

        # Not between 0 and 1 (2)
        try:
            parse_float_between_0_and_1(config.get_property_or_fail("x"))
            self.fail()
        except ValueError:
            self.assertTrue(True)
