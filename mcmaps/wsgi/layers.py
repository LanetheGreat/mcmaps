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

''' Generates the individual layers of a chunk based on MC version '''

import os
from http import HTTPStatus
from traceback import format_exc
from urllib.parse import parse_qs
from mcmaps.util.common import (
    HTTPServerException,
    verify_default_parameters,
    ensure_world_folder,
)
from mcmaps.util.wsgi import finalize_response

__all__ = ('application',)


def application(env, start_response):
    response_code = None
    response_headers = {}
    body = {}
    query = parse_qs(env['QUERY_STRING'])

    try:
        seed, version, x, z = verify_default_parameters(query)
        ensure_world_folder(os.path.join(env['CONTEXT_DOCUMENT_ROOT'], 'world_cache', seed))

    except Exception as err:
        if isinstance(err, HTTPServerException):
            response_code = err.code
        response_code = response_code or HTTPStatus.INTERNAL_SERVER_ERROR
        body['error'] = response_code.value
        body['message'] = str(err)
        if query.get('debug'):
            body['traceback'] = format_exc()
        yield from finalize_response(response_code, response_headers, start_response, body, query.get('debug'))
    else:
        response_code = HTTPStatus.OK

    yield from finalize_response(response_code, response_headers, start_response, body, query.get('debug'))
