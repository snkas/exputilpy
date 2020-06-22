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

import subprocess
import json
import sys
import re
from enum import Enum
from abc import ABC, abstractmethod


class OutputRedirect(Enum):
    CONSOLE = 0
    SILENT = 1
    PIPE_VARIABLE = 2
    SIMPLE_STRING = 3


class ShellExecResult:
    
    def __init__(self, return_code, output, process):
        self.return_code = return_code
        self.output = output
        self.process = process

    def __str__(self):
        return "ShellExecResult(return_code=%d, output=%s, process=%s)" % (
            self.return_code,
            self.output.strip(),
            str(self.process)
        )


class InvalidCommandError(Exception):
    """
    Error raised for when the command was invalid meaning that the command return anything else than 0-100.
    Invalid means for example:
     - Bash syntax was wrong
     - SSH could not connect
     - Command does not exist
     - Permission failed

    Attributes:
        message -- explanation of the exception
        sec -- Shell execution result
    """

    def __init__(self, message, sec):
        self.message = message
        self.sec = sec


class FailedCommandError(Exception):
    """
    Error raised for when the command failed (returned something in 1-100 instead of 0).

    Attributes:
        message -- explanation of the exception
        sec -- Shell execution result
    """

    def __init__(self, message, sec):
        self.message = message
        self.sec = sec


def local_shell_exec(command, sync=True, output_redirect=None, remote_exec_prefix_arr=None):
    """
    Execute the command in the local shell.

    :param command:                        Command (e.g., "ls")
    :param sync:                           True iff synchronized (i.e., wait till completion)
    :param output_redirect:                Where should the output be directed to
    :param remote_exec_prefix_arr:         Array of ["ssh", "a@b"] to prefix

    :return: 3-tuple of: (1) Return code of the process (-1 if async, as the process has not finished yet)
                         (2) If output_redirect is SIMPLE_STRING: a string combining stderr and stdout. Else: "".
                         (3) Handle to the called Popen process (if async, it is still running)
    """

    # Default output redirect
    if output_redirect is None:
        if sync:
            output_redirect = OutputRedirect.SIMPLE_STRING
        else:
            output_redirect = OutputRedirect.PIPE_VARIABLE

    # Small safety built-in
    stripped_command = command.strip()
    if stripped_command in ["rm -rf /", "rm -r /", "rm -rf ~", "rm -r ~", "rm -rf ~/", "rm -r ~/", "rm -rf *",
                            "rm -rf /*", "rm -rf ~/*", "rm -rf /*/", "rm -rf ~/*/", "rm -r *"]:
        raise ValueError("Refusal to remove root directory or home directory.")

    # Compose the actual command
    if remote_exec_prefix_arr is None:
        actual_command = command
        enable_shell = True
    else:
        actual_command = remote_exec_prefix_arr + [command]
        enable_shell = False

    # Determine output redirection
    if output_redirect == OutputRedirect.CONSOLE:
        set_stdout = sys.stdout
        set_stderr = sys.stderr
    elif output_redirect == OutputRedirect.SILENT:
        set_stdout = subprocess.DEVNULL
        set_stderr = subprocess.DEVNULL
    elif output_redirect == OutputRedirect.PIPE_VARIABLE:
        set_stdout = subprocess.PIPE
        set_stderr = subprocess.PIPE
    elif output_redirect == OutputRedirect.SIMPLE_STRING:
        if not sync:
            raise ValueError("Output cannot be redirected to a simple string if async.")
        set_stdout = subprocess.PIPE
        set_stderr = subprocess.STDOUT
    else:
        raise ValueError("Invalid output redirect value: " + str(output_redirect))

    # Execute the command
    if sync:
        proc = subprocess.run(actual_command, stdout=set_stdout, stderr=set_stderr, shell=enable_shell)
        if output_redirect == OutputRedirect.SIMPLE_STRING:
            output = proc.stdout.decode("utf-8")
        else:
            output = ""
        return ShellExecResult(proc.returncode, output, proc)

    else:
        proc = subprocess.Popen(actual_command, stdout=set_stdout, stderr=set_stderr, shell=enable_shell)
        return ShellExecResult(-1, "", proc)


class Shell(ABC):

    @staticmethod
    def _raise_if_invalid(res):
        if res.return_code > 100:
            raise InvalidCommandError(res.output, res)

    @staticmethod
    def _raise_if_invalid_or_fail(res):
        Shell._raise_if_invalid(res)
        if res.return_code != 0:
            raise FailedCommandError(res.output, res)

    @abstractmethod
    def exec(self, command, sync=True, output_redirect=None) -> ShellExecResult:
        """
        Execute the command.

        :param command:           Bash command
        :param sync:              True iff if the command should be done synchronously
        :param output_redirect:   Output redirection

        :return: ShellExecResult
        """
        pass  # Abstract method
    
    def perfect_exec(self, command, output_redirect=OutputRedirect.SIMPLE_STRING) -> ShellExecResult:
        """
        Execute the command synchronously and by default with output.
        Everything must have gone perfectly, else an exception is raised.
        This is for commands that only return 0 when they have executed successfully.
        
        FailedCommandError: if the command failed due to it returning not 0
        InvalidCommandError: if the command failed due to it being invalid (i.e., returned > 100)

        :param command: Bash command
        :param output_redirect:     Where should the output be directed to

        :return: ShellExecResult (with valid=True and return_code=0 guaranteed)
        """
        res = self.exec(command, sync=True, output_redirect=output_redirect)
        self._raise_if_invalid_or_fail(res)
        return res

    def valid_exec(self, command, output_redirect=OutputRedirect.SIMPLE_STRING) -> ShellExecResult:
        """
        Execute the command synchronously and by default with output.
        Only if the command is invalid (return code > 100), an exception is raised.
        This is for commands that have executed successfully (according to the user), but still return 1-100 (e.g., "screen -ls").
        
        InvalidCommandError: if the command failed due to it being invalid (i.e., returned > 100)

        :param command:             Bash command
        :param output_redirect:     Where should the output be directed to

        :return: ShellExecResult (with valid=True and return_code=0 or 1 guaranteed)
        """
        res = self.exec(command, sync=True, output_redirect=output_redirect)
        self._raise_if_invalid(res)
        return res

    def count_screens(self):
        res = self.valid_exec("screen -ls")
        return res.output.count("(Detached)")

    def detached_exec(self, command, keep_alive=False):
        return self.perfect_exec("screen -d -m bash -c \"%s%s\"" % (json.dumps(command)[1:-1], "; exec bash;" if keep_alive else ""))

    def killall(self, process_name):
        return self.valid_exec("killall %s" % process_name)

    def make_dir(self, directory):
        return self.perfect_exec("mkdir %s" % directory)

    def make_full_dir(self, directory):
        return self.perfect_exec("mkdir -p %s" % directory)

    def write_file(self, file_path, content=""):
        return self.perfect_exec("echo \"%s\" > %s" % (json.dumps(content)[1:-1], file_path))

    def read_file(self, file_path):
        res = self.perfect_exec("cat %s" % file_path)
        return res.output

    def move(self, from_path, to_path):
        return self.perfect_exec("mv %s %s" % (from_path, to_path))

    def remove(self, path):
        return self.perfect_exec("rm %s" % path)

    def remove_force(self, path):
        return self.perfect_exec("rm -f %s" % path)

    def remove_recursive(self, path):
        return self.perfect_exec("rm -r %s" % path)

    def remove_force_recursive(self, path):
        return self.perfect_exec("rm -rf %s" % path)

    def rsync(self, source_dir, target_dir, exclude=None, delete=False):
        exclude_str = ""
        if exclude is not None:
            for exclude_value in exclude:
                exclude_str += " --exclude %s" % exclude_value
        return self.perfect_exec("rsync -ravh %s %s%s%s" % (source_dir, target_dir, exclude_str, " --delete" if delete else ""))

    def copy_file(self, source_file, target_path):
        return self.perfect_exec("scp %s %s" % (source_file, target_path))

    def sed_replace_in_file_plain(self, target_file, search_term, replace_term):
        return self.perfect_exec("sed -i "
                                 "'s/"
                                 + re.escape(search_term).replace("/", "\\/")
                                 + "/"
                                 + replace_term.replace("\\", "\\\\").replace("/", "\\/").replace("&", "\\&")
                                 + "/g' " + target_file)

    def path_exists(self, path):
        res = self.valid_exec("if [ -d \"%s\" ]; then exit 0; else exit 1; fi" % path.replace('"', '\\"'))
        return res.return_code == 0

    def file_exists(self, file_path):
        res = self.valid_exec("if [ -f \"%s\" ]; then exit 0; else exit 1; fi" % file_path.replace('"', '\\"'))
        return res.return_code == 0

    def get_direct_sub_dirs(self, target_dir):
        res = self.perfect_exec("for f in %s/*; do if [ -d \"$f\" ]; then echo ${f}; fi; done" % target_dir)
        if len(res.output.strip()) == 0:
            return []
        else:
            return res.output.strip().split("\n")


class LocalShell(Shell):

    # def __init__(self):
    # For now, local shell is just default constructor

    def exec(self, command, sync=True, output_redirect=None) -> ShellExecResult:
        return local_shell_exec(command, sync, output_redirect)


class RemoteShell(Shell):

    def __init__(self, user, host):
        self.user = user
        self.host = host
        self.remote = ["ssh", "%s@%s" % (self.user, self.host)]

    def exec(self, command, sync=True, output_redirect=None) -> ShellExecResult:
        return local_shell_exec(command, sync, output_redirect, self.remote)
