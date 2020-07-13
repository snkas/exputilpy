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
import random
from exputil import *


class TestCsv(unittest.TestCase):

    def test_csv_normal(self):
        local_shell = LocalShell()
        local_shell.make_full_dir("temp")
        local_shell.write_file("temp/test.csv", "a,b,10,-9.3\nabc,def,-100000,30.24")
        data_columns = read_csv_direct_in_columns("temp/test.csv", "string,string,int,float")
        self.assertEqual(data_columns[0], ["a", "abc"])
        self.assertEqual(data_columns[1], ["b", "def"])
        self.assertEqual(data_columns[2], [10, -100000])
        self.assertEqual(data_columns[3], [-9.3, 30.24])
        local_shell.remove_force_recursive("temp")

    def test_csv_one_line(self):
        local_shell = LocalShell()
        local_shell.make_full_dir("temp")
        local_shell.write_file("temp/test.csv", "9998.8,-0")
        data_columns = read_csv_direct_in_columns("temp/test.csv", "pos_float,int")
        self.assertEqual(data_columns[0], [9998.8])
        self.assertEqual(data_columns[1], [0])
        local_shell.remove_force_recursive("temp")

    def test_csv_empty_line(self):
        local_shell = LocalShell()
        local_shell.make_full_dir("temp")
        local_shell.write_file("temp/test.csv", "")
        data_columns = read_csv_direct_in_columns("temp/test.csv", "string")
        self.assertEqual(data_columns[0], [""])
        local_shell.remove_force_recursive("temp")

    def test_csv_big(self):
        local_shell = LocalShell()
        local_shell.make_full_dir("temp")

        # Write a lot into the CSV file
        random.seed(99999999)
        values = [
            [],
            [],
            [],
            [],
            [],
            []
        ]
        with open("temp/test.csv", "w+") as f_out:
            for i in range(100000):
                values[0].append(i)
                values[1].append(random.randint(-99999, 999999))
                values[2].append(random.random() * 10000000.0 - 5000000.0)
                values[3].append("a" * random.randint(0, 30))
                values[4].append(random.randint(0, 999999))
                values[5].append(random.random() * 10000000.0)
                f_out.write(str(values[0][i]) + "," + str(values[1][i]) + "," + str(values[2][i]) + "," + values[3][i]
                            + "," + str(values[4][i]) + "," + str(values[5][i]) + "\n")

        # Read it in and compare
        data_columns = read_csv_direct_in_columns("temp/test.csv", "idx_int,int,float,string,pos_int,pos_float")
        self.assertEqual(data_columns, values)

        # Clean up
        local_shell.remove_force_recursive("temp")

    def test_negative(self):
        local_shell = LocalShell()
        local_shell.make_full_dir("temp")

        # Empty line wrong format
        try:
            local_shell.write_file("temp/test.csv", "")
            read_csv_direct_in_columns("temp/test.csv", "int")
            self.fail()
        except ValueError:
            self.assertTrue(True)

        # Empty line second wrong format
        try:
            local_shell.write_file("temp/test.csv", "")
            read_csv_direct_in_columns("temp/test.csv", "string,int")
            self.fail()
        except ValueError:
            self.assertTrue(True)

        # Wrong format (int)
        try:
            local_shell.write_file("temp/test.csv", "-9.3,56")
            read_csv_direct_in_columns("temp/test.csv", "int,int")
            self.fail()
        except ValueError:
            self.assertTrue(True)

        # Wrong format (float)
        try:
            local_shell.write_file("temp/test.csv", "-9.3,56,abc")
            read_csv_direct_in_columns("temp/test.csv", "string,int,float")
            self.fail()
        except ValueError:
            self.assertTrue(True)

        # Wrong format (positive float)
        try:
            local_shell.write_file("temp/test.csv", "-0.00001")
            read_csv_direct_in_columns("temp/test.csv", "pos_float")
            self.fail()
        except ValueError:
            self.assertTrue(True)

        # Wrong format (positive int)
        try:
            local_shell.write_file("temp/test.csv", "-1")
            read_csv_direct_in_columns("temp/test.csv", "pos_int")
            self.fail()
        except ValueError:
            self.assertTrue(True)

        # Wrong format (index int)
        try:
            local_shell.write_file("temp/test.csv", "1")
            read_csv_direct_in_columns("temp/test.csv", "idx_int")
            self.fail()
        except ValueError:
            self.assertTrue(True)

        # Too many on line
        try:
            local_shell.write_file("temp/test.csv", "-9.3,56,abc,9")
            read_csv_direct_in_columns("temp/test.csv", "float,int,string")
            self.fail()
        except ValueError:
            self.assertTrue(True)

        # Too few on line
        try:
            local_shell.write_file("temp/test.csv", "-9.3,56")
            read_csv_direct_in_columns("temp/test.csv", "float,int,int")
            self.fail()
        except ValueError:
            self.assertTrue(True)

        # Too few on line II
        try:
            local_shell.write_file("temp/test.csv", "-9.4")
            read_csv_direct_in_columns("temp/test.csv", "float,int")
            self.fail()
        except ValueError:
            self.assertTrue(True)

        # Invalid format I
        try:
            local_shell.write_file("temp/test.csv", "-9.4")
            read_csv_direct_in_columns("temp/test.csv", "floatint")
            self.fail()
        except ValueError:
            self.assertTrue(True)

        # Invalid format II
        try:
            local_shell.write_file("temp/test.csv", "-9.4,8")
            read_csv_direct_in_columns("temp/test.csv", "floatint")
            self.fail()
        except ValueError:
            self.assertTrue(True)

        # Invalid format III
        try:
            local_shell.write_file("temp/test.csv", "-9.4,8")
            read_csv_direct_in_columns("temp/test.csv", "string,tsring")
            self.fail()
        except ValueError:
            self.assertTrue(True)

        # Invalid format IV
        try:
            local_shell.write_file("temp/test.csv", "-9.4,8")
            read_csv_direct_in_columns("temp/test.csv", "string,")
            self.fail()
        except ValueError:
            self.assertTrue(True)

        # Invalid format V
        try:
            local_shell.write_file("temp/test.csv", "-9.4,8")
            read_csv_direct_in_columns("temp/test.csv", "float,in")
            self.fail()
        except ValueError:
            self.assertTrue(True)

        # Invalid format VI
        try:
            local_shell.write_file("temp/test.csv", "-9.4")
            read_csv_direct_in_columns("temp/test.csv", "")
            self.fail()
        except ValueError:
            self.assertTrue(True)

