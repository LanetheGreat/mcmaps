# Copyright 2020 Lane Shaw
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

''' Sub commands supported by the MC Maps library. '''

from argparse import ArgumentParser

__all__ = ['parser', 'subparsers']

# Top level command line argument parser
parser = ArgumentParser(
    prog='python -m mcmaps',
    description='MC Maps library command line.',
)
subparsers = parser.add_subparsers(help='sub-command help')

from . import maps  # @IgnorePep8 @UnresolvedImport
from . import webserver  # @IgnorePep8 @UnresolvedImport
