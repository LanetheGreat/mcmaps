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

''' Helper functions for common tasks in WSGI '''

__all__ = ['finalize_response']

import json


def finalize_response(code, headers, start_resp, body={}, debug=False):
    headers['Content-Type'] = 'application/json'
    start_resp('%s %s' % (code.value, code.phrase), list(headers.items()))
    yield json.dumps(body, indent=2 if debug else None).encode('us-ascii')
