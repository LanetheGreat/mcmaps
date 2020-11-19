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

import json, os
from http import HTTPStatus

from mcmaps.util.common import ensure_world_paths
from mcmaps.util.wsgi import (
    jsonify_exception,
    verify_default_parameters,
)

__all__ = ('application',)


@jsonify_exception
def application(env, start_response):
    response_code = HTTPStatus.OK
    response_headers = {}
    body = {}
    doc_root = env.get('CONTEXT_DOCUMENT_ROOT', os.getcwd())

    seed, version, world_type, x, z = verify_default_parameters(env['QUERY_STRING'])
    world_type_name = world_type.name.casefold()
    world_path = os.path.join(
        doc_root, 'world_cache',
        version, world_type_name, str(seed),
    )
    ensure_world_paths(world_path)

    body = json.dumps(body)
    response_headers['Content-Type'] = 'application/json'
    start_response(
        '%s %s' % (response_code.value, response_code.phrase),
        list(response_headers.items()),
    )
    yield body
