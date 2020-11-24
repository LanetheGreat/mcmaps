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

''' Generates a chunk's biome map based on MC version '''

import json, os, pickle
from http import HTTPStatus
from urllib.parse import parse_qs

from mcmaps.mc.chunks import hashChunkXZ
from mcmaps.mc.constants import WORLD_TYPE
from mcmaps.util.common import ensure_world_paths
from mcmaps.util.misc import SLONG_RANGE
from mcmaps.util.wsgi import jsonify_exception, BadRequest

__all__ = ('application',)

chunk_range = range(16)


def _ensure_generator(dim_folder, seed, world_type):
    generator_path = os.path.join(dim_folder, 'generator.pickled')
    if os.path.exists(generator_path):
        with open(generator_path, 'rb') as gen_file:
            return pickle.load(gen_file)

    # Load the generator and pickle a raw copy of it.
    from mcmaps.mc.biomes import initialize_all_biomes
    biome_generator, _ = initialize_all_biomes(seed, world_type)

    with open(generator_path, 'wb') as gen_file:
        pickle.dump(biome_generator, gen_file)

    return biome_generator


def _process_parameters(qs):
    query = parse_qs(qs)

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
        raise BadRequest('Invalid chunk z integer coordinate specified: ' + query['z'][0]) from None

    try:
        width = int(query['width'][0])
        if width <= 0:
            raise ValueError
    except (IndexError, KeyError):
        width = 1
    except ValueError:
        raise BadRequest('Invalid width length specified (must be greater than 0): ' + query['width'][0]) from None

    try:
        depth = int(query['depth'][0])
        if depth <= 0:
            raise ValueError
    except (IndexError, KeyError):
        depth = 1
    except ValueError:
        raise BadRequest('Invalid depth length specified (must be greater than 0): ' + query['depth'][0]) from None

    return seed, version, world_type, x, z, width, depth


@jsonify_exception
def application(env, start_response):
    global chunk_range
    response_code = HTTPStatus.OK
    response_headers = {}
    body = {}
    doc_root = env.get('CONTEXT_DOCUMENT_ROOT', os.getcwd())

    seed, version, world_type, chunkX, chunkZ, width, depth = _process_parameters(env['QUERY_STRING'])
    world_type_name = world_type.name.casefold()

    # World relative folders.
    world_path = os.path.join(
        doc_root, 'world_cache',
        version, world_type_name, str(seed),
    )
    dim_path = os.path.join(world_path, 'DIM0')

    ensure_world_paths(world_path)

    # Our list of chunks, indexed by their hash.
    chunk_list = {}
    x_range = range(chunkX, chunkX + width)
    z_range = range(chunkZ, chunkZ + depth)

    # Reserve generator variable for lazy loading later.
    generator = None

    # Load our existing biome data or generate it.
    for z in z_range:
        for x in x_range:
            chunk_hash = hashChunkXZ(x, z)
            hash_string = str(chunk_hash).rjust(20, '0')
            chunk_path = os.path.join(dim_path, 'biomes', hash_string + '.pickle')

            if os.path.exists(chunk_path):
                with open(chunk_path, 'rb') as pickle_file:
                    chunk = pickle.load(pickle_file)
            else:
                # Lazy load our generator.
                if not generator:
                    generator = _ensure_generator(dim_path, seed, world_type)

                # Generate the biome data and cache it.
                area = generator.get_area(x << 4, z << 4, 16, 16)
                biomes = []
                for az in chunk_range:
                    for ax in chunk_range:
                        biomes.append(area[ax][az])

                chunk = {
                    'x': x, 'z': z,
                    'hash': hash_string,
                    'biomes': sorted(map(int, set(biomes))),
                    'values': list(map(int, biomes)),
                }

                with open(chunk_path, 'wb') as pickle_file:
                    pickle.dump(chunk, pickle_file)

            # Add our chunk to the list of ones to export.
            chunk_list[chunk_hash] = chunk

    # Dump our chunk list as JSON.
    body = json.dumps([chunk for chunk in chunk_list.values()]).encode('us-ascii')
    response_headers['Content-Type'] = 'application/json'
    start_response(
        '%s %s' % (response_code.value, response_code.phrase),
        list(response_headers.items()),
    )
    yield body
