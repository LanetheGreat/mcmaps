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

import json
import os
import sys

__all__ = ('application',)


def application(env, start_response):
    env['python.version'] = tuple(sys.version_info)
    env['python.cwd'] = os.getcwd()
    response_header = [('Content-Type', 'application/json')]
    start_response('200 OK', response_header)
    yield json.dumps({
        'env': {
            key: str(value)
            for key, value in env.items()
        }
    }, sort_keys=True).encode('us-ascii')
