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

from exputil import *
import unittest


ENABLE_REMOTE_TEST = False
REMOTE_USER = "user"
REMOTE_HOST = "machine"


class TestFileDir(unittest.TestCase):

    def test_file(self):
        local_shell = LocalShell()
        local_shell.make_full_dir("temp")
        local_shell.remove_force("temp/test.txt")
        local_shell.write_file("temp/test.txt", "Test")
        self.assertTrue(local_shell.file_exists("temp/test.txt"))
        self.assertEqual("Test", local_shell.read_file("temp/test.txt").strip())
        local_shell.sed_replace_in_file_plain("temp/test.txt", "Tes", "ABc")
        self.assertEqual("ABct", local_shell.read_file("temp/test.txt").strip())
        with open("temp/test.txt", "w+") as f:
            writer = InstantWriter(f)
            writer.write("Ano/.ther testno/.ther")
        self.assertEqual("Ano/.ther testno/.ther", local_shell.read_file("temp/test.txt").strip())
        local_shell.sed_replace_in_file_plain("temp/test.txt", "no/.ther", " &blue/\\")
        self.assertEqual("A &blue/\\ test &blue/\\", local_shell.read_file("temp/test.txt").strip())
        self.assertTrue(local_shell.file_exists("temp/test.txt"))
        self.assertTrue(local_shell.move("temp/test.txt", "temp/test2.txt"))
        self.assertFalse(local_shell.file_exists("temp/test.txt"))
        self.assertTrue(local_shell.file_exists("temp/test2.txt"))
        local_shell.remove("temp/test2.txt")
        self.assertFalse(local_shell.file_exists("temp/test2.txt"))
        try:
            local_shell.read_file("temp/test.txt")
            self.assertTrue(False)
        except FailedCommandError:
            self.assertTrue(True)
        local_shell.remove_recursive("temp")

    def test_sed_replace(self):
        local_shell = LocalShell()
        local_shell.remove_force("temp")
        local_shell.make_full_dir("temp")
        local_shell.write_file("temp/testA.txt", "This is a blue world blue world")
        local_shell.sed_replace_in_file_plain("temp/testA.txt", "blue world", "green planet")
        self.assertEqual("This is a green planet green planet", local_shell.read_file("temp/testA.txt").strip())
        local_shell.remove("temp/testA.txt")
        local_shell.remove_recursive("temp")

    def test_dir(self):
        local_shell = LocalShell()
        local_shell.make_full_dir("temp")
        self.assertTrue(local_shell.path_exists("./temp/"))
        local_shell.make_full_dir("./temp/test")
        try:
            local_shell.make_dir("./temp/test1/test2")
            self.assertTrue(False)
        except FailedCommandError:
            self.assertTrue(True)
        local_shell.make_full_dir("./temp/test1/test2")
        sub_dirs = local_shell.get_direct_sub_dirs("./temp")
        self.assertEqual(2, len(sub_dirs))
        self.assertTrue("./temp/test" in sub_dirs)
        self.assertTrue("./temp/test1" in sub_dirs)
        self.assertEqual(len(local_shell.get_direct_sub_dirs("./temp/test1")), 1)
        self.assertEqual(len(local_shell.get_direct_sub_dirs("./temp/test1/test2")), 0)
        local_shell.remove_recursive("temp/test")
        local_shell.remove_force_recursive("temp/test1")
        local_shell.remove_recursive("temp")
        self.assertFalse(local_shell.path_exists("temp"))

    def test_rsync_and_copy_file(self):
        local_shell = LocalShell()
        local_shell.make_full_dir("temp")
        local_shell.write_file("temp/test.txt", "Test1")
        local_shell.write_file("temp/a.txt", "Test2")
        local_shell.write_file("temp/b.txt", "Test3")
        local_shell.rsync("temp/", "temp2/", exclude=["a.txt", "b.txt"], delete=True)
        self.assertTrue(local_shell.file_exists("temp2/test.txt"))
        self.assertFalse(local_shell.file_exists("temp2/a.txt"))
        self.assertFalse(local_shell.file_exists("temp2/b.txt"))
        local_shell.copy_file("temp/a.txt", "temp2")
        self.assertTrue(local_shell.file_exists("temp/a.txt"))
        local_shell.remove_recursive("temp2")
        local_shell.remove_recursive("temp")

    def test_remote_rsync_and_copy_file(self):
        if ENABLE_REMOTE_TEST:
            local_shell = LocalShell()
            remote_shell = RemoteShell(REMOTE_USER, REMOTE_HOST)
            local_shell.make_full_dir("temp")
            local_shell.write_file("temp/test.txt", "Test1")
            local_shell.write_file("temp/a.txt", "Test2")
            local_shell.write_file("temp/b.txt", "Test3")
            local_shell.rsync("temp/", "%s@%s:~/temp/" % (REMOTE_USER, REMOTE_HOST),
                              exclude=["a.txt", "b.txt"], delete=True)
            self.assertTrue(remote_shell.file_exists("temp/test.txt"))
            self.assertFalse(remote_shell.file_exists("temp/a.txt"))
            self.assertFalse(remote_shell.file_exists("temp/b.txt"))
            local_shell.copy_file("temp/a.txt", "%s@%s:~/temp" % (REMOTE_USER, REMOTE_HOST))
            self.assertTrue(remote_shell.file_exists("temp/a.txt"))
            remote_shell.remove_recursive("~/temp")
            local_shell.remove_recursive("temp")

    def test_properties_loader_success(self):
        local_shell = LocalShell()
        local_shell.make_full_dir("temp")
        local_shell.write_file("temp/test.txt", "a=b\n#c=d\n   \ny=7\nm=\"above\"\nX='ll'")
        config = PropertiesConfig("temp/test.txt")
        self.assertEqual(4, config.get_num_properties())
        self.assertEqual("b", config.get_property_or_fail("a"))
        self.assertEqual("7", config.get_property_or_fail("y"))
        self.assertEqual("above", config.get_property_or_fail("m"))
        self.assertEqual("'ll'", config.get_property_or_fail("X"))
        local_shell.remove_recursive("temp")

    def test_properties_loader_failure(self):
        local_shell = LocalShell()
        local_shell.make_full_dir("temp")
        local_shell.write_file("temp/test1.txt", "a\nb=9")
        local_shell.write_file("temp/test2.txt", "a=5\na=9")
        local_shell.write_file("temp/test3.txt", "a=")

        try:
            PropertiesConfig("temp/test1.txt")
            self.assertTrue(False)
        except ValueError as e:
            self.assertEqual(e.args[0], "Not a key=value pair: a")

        try:
            PropertiesConfig("temp/test2.txt")
            self.assertTrue(False)
        except ValueError as e:
            self.assertEqual(e.args[0], "Duplicate key: a")

        try:
            PropertiesConfig("temp/test3.txt")
            self.assertTrue(False)
        except ValueError as e:
            self.assertEqual(e.args[0], "Empty value at key: a")

        # Remove temp recursive
        local_shell.remove_recursive("temp")
