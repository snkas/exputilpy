#!/usr/bin/env bash

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

rm -rf temp || exit 1
mkdir temp || exit 1
tar --exclude "temp" -zcf temp/python-exputil.tar.gz ./ || exit 1
pip3 install temp/python-exputil.tar.gz || exit 1
rm -r temp || exit 1
