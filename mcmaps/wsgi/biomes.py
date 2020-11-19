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
from PIL import Image

from mcmaps.mc.chunks import hashChunkXZ
from mcmaps.util.common import ensure_world_paths
from mcmaps.util.wsgi import (
    jsonify_exception,
    verify_default_parameters,
)

__all__ = ('application',)


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


@jsonify_exception
def application(env, start_response):
    response_code = HTTPStatus.OK
    response_headers = {}
    body = {}
    doc_root = env.get('CONTEXT_DOCUMENT_ROOT', os.getcwd())

    seed, version, world_type, x, z = verify_default_parameters(env['QUERY_STRING'])
    world_type_name = world_type.name.casefold()
    chunk_hash = str(hashChunkXZ(x, z)).rjust(20, '0')

    # World relative folders.
    world_path = os.path.join(
        doc_root, 'world_cache',
        version, world_type_name, str(seed),
    )
    dim_path = os.path.join(world_path, 'DIM0')
    image_comp = (version, world_type_name, str(seed), 'DIM0', 'biomes', 'img', chunk_hash)
    chunk_path = os.path.join(dim_path, 'biomes', chunk_hash + '.json')
    image_path = os.path.join(dim_path, 'biomes', 'img', chunk_hash + '.png')

    ensure_world_paths(world_path)

    # Load our existing biome data if it was already generated.
    if os.path.exists(chunk_path):
        with open(chunk_path, 'rb') as json_file:
            body = json_file.read()

        response_headers['Content-Type'] = 'application/json'
        start_response(
            '%s %s' % (response_code.value, response_code.phrase),
            list(response_headers.items()),
        )
        yield body
        return

    # Load our cached generator, if it was already generated itself.
    generator = _ensure_generator(dim_path, seed, world_type)

    # Generate the biome data and cache it.
    r = range(16)
    area = generator.get_area(x << 4, z << 4, 16, 16)
    biomes = []
    for az in r:
        for ax in r:
            biomes.append(area[ax][az])

    # Generate the chunk image and save it.
    Image.frombytes(
        mode='RGB',
        size=(16, 16),
        data=b''.join(bytes(biome.color) for biome in biomes),
    ).save(image_path, optimize=True)

    # Create our API JSON data and cache it.
    body = json.dumps({
        'x': x, 'z': z,
        'hash': chunk_hash,
        'biomes': sorted(map(int, set(biomes))),
        'values': list(map(int, biomes)),
        'image': '/' + '/'.join(('cache', *image_comp)) + '.png',
    }).encode('us-ascii')

    with open(chunk_path, 'wb') as json_file:
        json_file.write(body)

    response_headers['Content-Type'] = 'application/json'
    start_response(
        '%s %s' % (response_code.value, response_code.phrase),
        list(response_headers.items()),
    )
    yield body
