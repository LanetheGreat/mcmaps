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

from http import HTTPStatus
from urllib.parse import parse_qs

from mcmaps.mc.constants import WORLD_TYPE
from mcmaps.util.misc import SLONG_RANGE

__all__ = [
    'BadRequest',
    'jsonify_exception',
    'verify_default_parameters',
]


class HTTPServerException(Exception):
    code = 0


class BadRequest(HTTPServerException):
    code = HTTPStatus.BAD_REQUEST


def verify_default_parameters(query):
    query = parse_qs(query)

    if not query.get('seed'):
        raise BadRequest('No Minecraft seed specified. Missing parameter "seed"')
    else:
        try:
            seed = int(query['seed'][0])
            if seed not in SLONG_RANGE:
                raise ValueError
        except ValueError:
            raise BadRequest('Invalid numeric Minecraft seed specified: ' + query['seed'][0]) from None

    if not query.get('version'):
        raise BadRequest('No Minecraft version specified. Missing parameter "version"')
    version = query['version'][0]

    world_type = str(query.get('wtype', ['DEFAULT'])[0]).upper()
    if world_type not in WORLD_TYPE.__members__:  # @UndefinedVariable
        raise BadRequest('Invalid world type specified: ' + query['wtype'][0]) from None
    world_type = WORLD_TYPE.__members__[world_type]  # @UndefinedVariable

    if not query.get('x'):
        raise BadRequest('No chunk x coordinate specified. Missing parameter "x"')
    try:
        x = int(query['x'][0])
    except ValueError:
        raise BadRequest('Invalid chunk x integer coordinate specified: ' + query['x'][0]) from None

    if not query.get('z'):
        raise BadRequest('No chunk z coordinate specified. Missing parameter "z"')
    try:
        z = int(query['z'][0])
    except ValueError:
        raise BadRequest('Invalid chunk y integer coordinate specified: ' + query['z'][0]) from None

    return seed, version, world_type, x, z


def jsonify_exception(application):
    import json, os
    from functools import wraps
    from traceback import format_exc

    @wraps(application)
    def wrapped_app(env, start_response):
        try:
            yield from application(env, start_response)
        except Exception as err:
            if isinstance(err, HTTPServerException):
                response_code = err.code
            else:
                response_code = HTTPStatus.INTERNAL_SERVER_ERROR
            body = {
                'error': response_code.value,
                'message': str(err),
            }
            if os.environ.get('DEBUG_HTTP'):
                body['traceback'] = format_exc()

            start_response(
                '%s %s' % (response_code.value, response_code.phrase),
                [('Content-Type', 'application/json')],
            )
            yield json.dumps(body, indent=2 if os.environ.get('DEBUG_HTTP') else None).encode('us-ascii')

    return wrapped_app
