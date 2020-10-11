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

''' Common functionality used by MC Maps WSGI script endpoints '''

from http import HTTPStatus
from os import makedirs
from os.path import join

from .misc import SLONG_RANGE


class HTTPServerException(Exception):
    code = 0


class BadRequest(HTTPServerException):
    code = HTTPStatus.BAD_REQUEST


def verify_default_parameters(query):
    if not query.get('seed'):
        raise BadRequest('No Minecraft seed specified. Missing parameter "seed"')
    else:
        try:
            seed = int(query['seed'][0])
            if seed not in SLONG_RANGE:
                raise ValueError
        except ValueError:
            raise BadRequest('Invalid numeric Minecraft seed specified: ' + query['seed'][0]) from None

    version = query.get('version')
    if not version:
        raise BadRequest('No Minecraft version specified. Missing parameter "version"')

    if not query.get('x'):
        raise BadRequest('No chunk x coordinate specified. Missing parameter "x"')
    else:
        try:
            x = int(query['x'][0])
        except ValueError:
            raise BadRequest('Invalid chunk x integer coordinate specified: ' + query['x'][0]) from None

    if not query.get('z'):
        raise BadRequest('No chunk z coordinate specified. Missing parameter "z"')
    else:
        try:
            z = int(query['z'][0])
        except ValueError:
            raise BadRequest('Invalid chunk y integer coordinate specified: ' + query['z'][0]) from None

    return seed, version, x, z


def _ensure_dim_folders(world_path, dim):
    # Create the blocks, layers, and biomes maps folders
    makedirs(join(world_path, dim, 'blocks'), exist_ok=True)
    makedirs(join(world_path, dim, 'layers'), exist_ok=True)
    makedirs(join(world_path, dim, 'biomes'), exist_ok=True)


def ensure_world_folder(path):
    # Create the seeds project folder
    makedirs(path, exist_ok=True)

    # Make dimensions for Overworld, Nether, and the End.
    _ensure_dim_folders(path, 'DIM0')
    _ensure_dim_folders(path, 'DIM-1')
    _ensure_dim_folders(path, 'DIM1')
