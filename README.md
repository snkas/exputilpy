# Experiment utilities

[![build](https://github.com/snkas/exputilpy/workflows/build/badge.svg)](https://github.com/snkas/exputilpy/actions?query=workflow%3Abuild+branch%3Amaster) [![codecov](https://codecov.io/gh/snkas/exputilpy/branch/master/graph/badge.svg)](https://codecov.io/gh/snkas/exputilpy)

A Python wrapper for utilities to automate running experiments, in particular with relation to bash. For example, to copy over files, run commands, check activity, etc.. Please note that it is written with a Linux bash in mind, so some functionality might not work on e.g., MacOS.

**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. (see also the MIT License in ./LICENSE).**

## Installation

**Requirements**
* Python 3.7+
* (optional) pytest (`pip3 install pytest`)
* (optional) coverage (`pip3 install coverage`)

**Option 1**

```bash
$ pip3 install git+https://github.com/snkas/exputilpy.git
```

You can now include it using: `import exputil`

**Option 2**

Clone/download this Git repository. Then, execute the following to install the package locally:

```bash
$ bash install_local.sh
```

You can now include it using: `import exputil`

## Getting started

There are many things to do, for example to check how many screens are running:

```python
import exputil

local_shell = exputil.LocalShell()
print("There are %d screens active." % local_shell.count_screens())

remote_shell = exputil.RemoteShell("user", "example.com")
print("There are %d screens active on the remote." % remote_shell.count_screens())
```

## Testing

Run all tests (local version):
```bash
$ python3 -m pytest
```

Run all tests (global pip3-installed version):
```bash
$ pytest
```

Calculate coverage locally (output in `htmlcov/`):
```bash
$ bash calculate_coverage.sh
```
