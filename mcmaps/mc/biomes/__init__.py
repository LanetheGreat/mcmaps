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

''' Library classes for Biome layer generation. '''

from . import _abc
from . import island
from . import misc
from . import river
from . import zoom
from ._abc import *
from .island import *
from .misc import *
from .river import *
from .zoom import *
from mcmaps.mc.constants import WORLD_TYPE

__all__ = [
    *_abc.__all__,
    *island.__all__,
    *misc.__all__,
    *river.__all__,
    *zoom.__all__,
    'initialize_all_biomes',
]

_ISLAND_LAYERS = (
    (IslandLayer, 1),
    (FuzzyZoomLayer, 2000),
    (AddIslandLayer, 1),
    (ZoomLayer, 2001),
    (AddIslandLayer, 2),
    (AddSnowLayer, 2),
    (ZoomLayer, 2002),
    (AddIslandLayer, 3),
    (ZoomLayer, 2003),
    (AddIslandLayer, 4),
    (AddMushroomIslandLayer, 5),
)


def initialize_all_biomes(world_seed, world_type, _debug=None):
    global _BIOME_LAYERS
    from copy import copy

    base_zoom = 6 if world_type is WORLD_TYPE.LARGE_BIOME else 4

    # Initialize our island and ocean biome generators.
    island_layer = None
    for layer, seed in _ISLAND_LAYERS:
        island_layer = layer(seed, child=island_layer, _debug=_debug)

    # Initialize our river and landmass biome generators.
    river_init_layer = ZoomLayer.zoom(
        1000,
        child=RiverInitLayer(100, island_layer, _debug=_debug),
        zoom_count=base_zoom + 2,
        _debug=_debug,
    )
    river_layer = SmoothLayer(
        1000,
        child=RiverLayer(
            1,
            child=river_init_layer,
            _debug=_debug,
        ),
        _debug=_debug,
    )
    land_layer = HillsLayer(
        1000,
        child=ZoomLayer.zoom(
            1000,
            child=BiomeInitLayer(200, child=island_layer, world_type=world_type, _debug=_debug),
            zoom_count=2,
            _debug=_debug,
        ),
        _debug=_debug,
    )

    # Zoom out our landmass biomes.
    for zoom in range(base_zoom):
        land_layer = ZoomLayer(1000 + zoom, child=land_layer, _debug=_debug)

        if zoom == 0:
            land_layer = AddIslandLayer(3, child=land_layer, _debug=_debug)

        if zoom == 1:
            land_layer = ShoreLayer(1000, child=land_layer, _debug=_debug)
            land_layer = SwampRiverLayer(1000, child=land_layer, _debug=_debug)

    # Merge the river and landmass generators and create a biome noise layer.
    block_biome_layer = RiverMixerLayer(
        100,
        child=SmoothLayer(1000, land_layer, _debug=_debug),
        child_river=river_layer,
        _debug=_debug,
    )
    biome_noise_layer = VoronoiZoomLayer(10, child=copy(block_biome_layer), _debug=_debug)

    # Calculate the layers seeds. (Recursively calculates all the wrapped child layers' seeds)
    block_biome_layer.init_world_seed(world_seed)
    biome_noise_layer.init_world_seed(world_seed)

    return block_biome_layer, biome_noise_layer
