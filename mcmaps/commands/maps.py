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

''' Command line for creating map data. '''

__all__ = ['generate_image']

from pathlib import Path

from . import subparsers  # @UnresolvedImport
from mcmaps.mc.constants import WORLD_TYPE
from PIL import Image

worker_generator = None


def image_worker_init(generator):
    global worker_generator
    worker_generator = generator


def image_worker(x, z, w, d):
    global worker_generator
    chunk_range = range(16)

    # Generate the biome data.
    area = worker_generator.get_area(x, z, 16, 16)

    # Create a single unified list of biome values per chunk.
    biomes = []
    for az in chunk_range:
        for ax in chunk_range:
            biomes.append(area[ax][az])

    # Create a chunk image from the biome color values and return it.
    return x, z, b''.join(map(bytes, (biome.color for biome in biomes)))


def generate_image(args):
    from mcmaps.java.string import hashCode
    from mcmaps.mc.biomes import initialize_all_biomes
    from time import perf_counter
    from multiprocessing import Pool

    # Try to parse our seed as either a 64-bit long or hash a string.
    try:
        seed = int(args.seed)
    except ValueError:
        seed = hashCode(args.seed)
    else:
        if seed not in range(-2**63, 2**63):
            raise ValueError('Invalid seed: ' + args.seed)

    # Pick either the block biome layers or the rainfall/temperature index layers.
    layers_generator = initialize_all_biomes(seed, args.type)[args.index]

    # Round our map corners to the nearest chunk boundary.
    min_x = args.x - (args.x % 16)
    min_z = args.z - (args.z % 16)
    width = args.width - (args.width % 16)
    depth = args.depth - (args.depth % 16)

    if args.width % 16:
        width += 16
    if args.depth % 16:
        depth += 16

    max_x = min_x + width
    max_z = min_z + depth

    x_range = range(min_x, max_x + 1, 16)
    z_range = range(min_z, max_z + 1, 16)

    # Setup our full image map.
    map_image = Image.new('RGB', (width, depth))

    # Start timing things.
    start_time = perf_counter()

    image_pool = Pool(
        initializer=image_worker_init,
        initargs=(layers_generator, ),
    )
    work_args = []

    # Preload all of our worker arguments.
    for z in z_range:
        for x in x_range:
            work_args.append((x, z, 16, 16))

    try:
        # Process the results from each worker process into an image.
        for x, z, image_bytes in image_pool.starmap(image_worker, work_args):
            map_image.paste(
                Image.frombytes('RGB', (16, 16), image_bytes),
                box=(x - min_x, z - min_z),
            )
    finally:
        image_pool.close()
        image_pool.join()

    # Save the new map to an image file.
    map_image.save(args.outfile, format='PNG', optimize=True)

    # Print timing.
    seconds = int(perf_counter() - start_time) + 1
    print('Generated %sx%s map in %s second(s).' % (width, depth, seconds))


MAP_CMDS = {
    'image': generate_image,
}


def _get_world_type(world_type):
    return WORLD_TYPE.__members__[str(world_type).upper()]  # @UndefinedVariable


server_cmd = subparsers.add_parser('maps', help='map generation commands')
server_cmd.add_argument('-s', '--seed', required=True)
server_cmd.add_argument('-i', '--index', action='store_true')
server_cmd.add_argument('-t', '--type', type=_get_world_type, default=WORLD_TYPE.DEFAULT, choices=WORLD_TYPE.__members__)  # @UndefinedVariable
server_cmd.add_argument('-x', type=int, default=-192)
server_cmd.add_argument('-z', type=int, default=-192)
server_cmd.add_argument('-w', '--width', type=int, default=384)
server_cmd.add_argument('-d', '--depth', type=int, default=384)
server_cmd.add_argument('-o', '--outfile', type=Path, default='map.png')
server_cmd.add_argument('command', metavar='command', type=str.lower, choices=MAP_CMDS, help='Supported commands: ' + ', '.join(MAP_CMDS))
server_cmd.set_defaults(command_func=lambda x: MAP_CMDS[x.command](x))
