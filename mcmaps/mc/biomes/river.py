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

''' River layer generation. '''

from copy import copy
from ctypes import c_int64

from ._abc import BaseLayer
from mcmaps.mc.constants import BIOME_ID

__all__ = [
    'RiverInitLayer', 'RiverLayer', 'SwampRiverLayer',
    'RiverMixerLayer',
]


class RiverInitLayer(BaseLayer):

    def get_area(self, x_pos, z_pos, x_width, z_depth):
        biome_values = [[BIOME_ID.OCEAN] * z_depth for _ in range(x_width)]
        child_values = self.child_layer.get_area(
            x_pos, z_pos, x_width, z_depth,
        )

        for z in range(z_depth):
            for x in range(x_width):
                self.init_chunk_seed(x_pos + x, z_pos + z)

                if child_values[x][z] != BIOME_ID.OCEAN:
                    # Randomly either BIOME_ID.DESERT or BIOME_ID.HILLS_EXTREME.
                    biome_values[x][z] = BIOME_ID(BIOME_ID.DESERT + self.nextInt(2))
                else:
                    biome_values[x][z] = BIOME_ID.OCEAN

        if self._debug:
            self._output_debug_data('RiverInit', x_pos, z_pos, x_width, z_depth, biome_values)

        return biome_values


class RiverLayer(BaseLayer):

    def get_area(self, x_pos, z_pos, x_width, z_depth):
        biome_values = [[BIOME_ID.OCEAN] * z_depth for _ in range(x_width)]
        child_values = self.child_layer.get_area(
            x_pos - 1, z_pos - 1,
            x_width + 2, z_depth + 2,
        )

        for z in range(z_depth):
            for x in range(x_width):

                # T=Top,  M=Middle, B=Bottom
                # L=Left, C=Center, R=Right
                #
                # [   | TC |   ]
                # [---+----+---]
                # [ML | MC | MR]
                # [---+----+---]
                # [   | BC |   ]
                center_value = child_values[x + 1][z + 1]  # MC
                value_matrix = (
                    child_values[x + 1][z + 0],  # TC
                    child_values[x + 2][z + 1],  # ML
                    child_values[x + 0][z + 1],  # MR
                    child_values[x + 1][z + 2],  # BC
                    center_value,
                )

                if BIOME_ID.OCEAN not in value_matrix and\
                   all(value == center_value for value in value_matrix):
                    biome_values[x][z] = BIOME_ID.NONE
                else:
                    biome_values[x][z] = BIOME_ID.RIVER

        if self._debug:
            self._output_debug_data('River', x_pos, z_pos, x_width, z_depth, biome_values)

        return biome_values


class SwampRiverLayer(BaseLayer):

    def get_area(self, x_pos, z_pos, x_width, z_depth):
        biome_values = [[BIOME_ID.OCEAN] * z_depth for _ in range(x_width)]
        child_values = self.child_layer.get_area(
            x_pos - 1, z_pos - 1,
            x_width + 2, z_depth + 2,
        )
        jungle_biomes = (BIOME_ID.JUNGLE, BIOME_ID.HILLS_JUNGLE)

        for z in range(z_depth):
            for x in range(x_width):
                self.init_chunk_seed(x_pos + x, z_pos + z)

                # Grab the diagonal biome value to us, up 1 X and over 1 Z.
                adj_value = child_values[x + 1][z + 1]
                if (
                    (adj_value is not BIOME_ID.SWAMP or self.nextInt(6)) and
                    (adj_value not in jungle_biomes or self.nextInt(8))
                ):
                    biome_values[x][z] = adj_value
                else:
                    biome_values[x][z] = BIOME_ID.RIVER

        if self._debug:
            self._output_debug_data('SwampRiver', x_pos, z_pos, x_width, z_depth, biome_values)

        return biome_values


class RiverMixerLayer(BaseLayer):
    __slots__ = ('child_river_layer', )

    def __init__(self, layer_seed, child=None, child_river=None, _debug=None):
        BaseLayer.__init__(self, layer_seed, child=child, _debug=_debug)
        self.child_river_layer = child_river

    def __repr__(self):
        values = (
            ('world seed', self.world_seed.value),
            ('chunk seed', self.chunk_seed.value),
            ('layer seed', self.layer_seed.value),
            ('land child layer', self.child_layer),
            ('river child layer', self.child_river_layer),
        )

        return '%s(%s)' % (
            self.__class__.__name__,
            ', '.join('%s=%s' % value for value in values),
        )

    def __getstate__(self):
        return (
            '1.6.4',
            self.world_seed.value,
            self.layer_seed.value,
            self.chunk_seed.value,
            self.child_layer,
            self.child_river_layer,
        )

    def __setstate__(self, state):
        version = state[0]  # @UnusedVariable
        self.world_seed = c_int64(state[1])
        self.layer_seed = c_int64(state[2])
        self.chunk_seed = c_int64(state[3])
        self.child_layer = state[4]
        self.child_river_layer = state[5]
        self._debug = None

    def __copy__(self):
        obj = BaseLayer.__copy__(self)
        obj.child_river_layer = copy(self.child_river_layer)
        return obj

    def init_world_seed(self, world_seed):
        self.world_seed.value = world_seed
        layer_seed = self.layer_seed.value

        self.child_layer.init_world_seed(world_seed)
        self.child_river_layer.init_world_seed(world_seed)

        self.world_seed.value *= self.world_seed.value * 6364136223846793005 + 1442695040888963407
        self.world_seed.value += layer_seed

        self.world_seed.value *= self.world_seed.value * 6364136223846793005 + 1442695040888963407
        self.world_seed.value += layer_seed

        self.world_seed.value *= self.world_seed.value * 6364136223846793005 + 1442695040888963407
        self.world_seed.value += layer_seed

    def get_area(self, x_pos, z_pos, x_width, z_depth):
        biome_values = [[BIOME_ID.OCEAN] * z_depth for _ in range(x_width)]
        child_biome_values = self.child_layer.get_area(
            x_pos, z_pos, x_width, z_depth,
        )
        child_river_values = self.child_river_layer.get_area(
            x_pos, z_pos, x_width, z_depth,
        )
        mushroom_biomes = (
            BIOME_ID.MUSHROOM_ISLAND,
            BIOME_ID.MUSHROOM_BEACH,
        )

        for z in range(z_depth):
            for x in range(x_width):
                biome_value = child_biome_values[x][z]

                if biome_value is BIOME_ID.OCEAN:
                    biome_values[x][z] = biome_value

                elif child_river_values[x][z] >= BIOME_ID.OCEAN:
                    if biome_value is BIOME_ID.PLAINS_ICE:
                        biome_values[x][z] = BIOME_ID.RIVER_FROZEN
                    elif biome_value not in mushroom_biomes:
                        biome_values[x][z] = child_river_values[x][z]
                    else:
                        biome_values[x][z] = BIOME_ID.MUSHROOM_BEACH

                else:
                    biome_values[x][z] = biome_value

        if self._debug:
            self._output_debug_data('RiverMixer', x_pos, z_pos, x_width, z_depth, biome_values)

        return biome_values
