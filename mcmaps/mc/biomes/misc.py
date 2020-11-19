# Copyright 2020 Lane Shaw
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

''' Miscellaneous other layers used in biome generation. '''

from copy import copy
from ctypes import c_int64

from ._abc import BaseLayer
from mcmaps.mc.constants import BIOME_ID, WORLD_TYPE

__all__ = [
    'AddSnowLayer', 'BiomeInitLayer',
    'HillsLayer', 'SmoothLayer',
]


class AddSnowLayer(BaseLayer):

    def get_area(self, x_pos, z_pos, x_width, z_depth):
        biome_values = [[BIOME_ID.OCEAN] * z_depth for _ in range(x_width)]
        child_values = self.child_layer.get_area(
            x_pos - 1, z_pos - 1,
            x_width + 2, z_depth + 2,
        )

        for z in range(z_depth):
            for x in range(x_width):
                self.init_chunk_seed(x_pos + x, z_pos + z)
                next_value = child_values[x + 1][z + 1]

                if next_value is not BIOME_ID.OCEAN:
                    if not self.nextInt(5):
                        next_value = BIOME_ID.PLAINS_ICE
                    else:
                        next_value = BIOME_ID.PLAINS

                biome_values[x][z] = next_value

        if self._debug:
            self._output_debug_data('AddSnow', x_pos, z_pos, x_width, z_depth, biome_values)

        return biome_values


class BiomeInitLayer(BaseLayer):
    __slots__ = ('allowed_biomes',)

    def __init__(self, layer_seed, child=None, world_type=WORLD_TYPE.DEFAULT, _debug=None):
        BaseLayer.__init__(self, layer_seed, child=child, _debug=_debug)
        if world_type == WORLD_TYPE.DEFAULT_1_1:
            self.allowed_biomes = (
                BIOME_ID.DESERT,
                BIOME_ID.FOREST,
                BIOME_ID.HILLS_EXTREME,
                BIOME_ID.SWAMP,
                BIOME_ID.PLAINS,
                BIOME_ID.TAIGA,
            )

        else:
            self.allowed_biomes = (
                BIOME_ID.DESERT,
                BIOME_ID.FOREST,
                BIOME_ID.HILLS_EXTREME,
                BIOME_ID.SWAMP,
                BIOME_ID.PLAINS,
                BIOME_ID.TAIGA,
                BIOME_ID.JUNGLE,
            )

    def __repr__(self):
        values = (
            ('world seed', self.world_seed.value),
            ('chunk seed', self.chunk_seed.value),
            ('layer seed', self.layer_seed.value),
            ('allowed biomes', self.allowed_biomes),
            ('child', self.child_layer),
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
            self.allowed_biomes,
            self.child_layer,
        )

    def __setstate__(self, state):
        version = state[0]  # @UnusedVariable
        self.world_seed = c_int64(state[1])
        self.layer_seed = c_int64(state[2])
        self.chunk_seed = c_int64(state[3])
        self.allowed_biomes = state[4]
        self.child_layer = state[5]
        self._debug = None

    def __copy__(self):
        obj = BaseLayer.__copy__(self)
        obj.allowed_biomes = copy(self.allowed_biomes)
        return obj

    def get_area(self, x_pos, z_pos, x_width, z_depth):
        biome_values = [[BIOME_ID.OCEAN] * z_depth for _ in range(x_width)]
        child_values = self.child_layer.get_area(
            x_pos, z_pos, x_width, z_depth,
        )
        preserve_biomes = (
            BIOME_ID.OCEAN,
            BIOME_ID.MUSHROOM_ISLAND,
        )

        for z in range(z_depth):
            for x in range(x_width):
                self.init_chunk_seed(x_pos + x, z_pos + z)
                next_value = child_values[x][z]

                if next_value in preserve_biomes:
                    biome_values[x][z] = next_value

                elif next_value is BIOME_ID.PLAINS:
                    biome_index = self.nextInt(len(self.allowed_biomes))
                    biome_values[x][z] = self.allowed_biomes[biome_index]

                elif self.allowed_biomes[self.nextInt(len(self.allowed_biomes))] is BIOME_ID.TAIGA:
                    biome_values[x][z] = BIOME_ID.TAIGA

                else:
                    biome_values[x][z] = BIOME_ID.PLAINS_ICE

        if self._debug:
            self._output_debug_data('Biome', x_pos, z_pos, x_width, z_depth, biome_values)

        return biome_values


class HillsLayer(BaseLayer):
    HILLS_MAP = {
        BIOME_ID.DESERT:     BIOME_ID.HILLS_DESERT,
        BIOME_ID.FOREST:     BIOME_ID.HILLS_FOREST,
        BIOME_ID.TAIGA:      BIOME_ID.HILLS_TAIGA,
        BIOME_ID.PLAINS:     BIOME_ID.FOREST,
        BIOME_ID.PLAINS_ICE: BIOME_ID.HILLS_EXTREME_ICE,
        BIOME_ID.JUNGLE:     BIOME_ID.HILLS_JUNGLE,
    }

    def get_area(self, x_pos, z_pos, x_width, z_depth):
        biome_values = [[BIOME_ID.OCEAN] * z_depth for _ in range(x_width)]
        child_values = self.child_layer.get_area(
            x_pos - 1, z_pos - 1,
            x_width + 2, z_depth + 2,
        )

        for z in range(z_depth):
            for x in range(x_width):
                self.init_chunk_seed(x_pos + x, z_pos + z)
                next_value = child_values[x + 1][z + 1]

                if not self.nextInt(3):
                    hill_value = self.HILLS_MAP.get(next_value, next_value)

                    if hill_value == next_value:
                        biome_values[x][z] = next_value
                    else:
                        # T=Top,  M=Middle, B=Bottom
                        # L=Left, C=Center, R=Right
                        #
                        # [   | TC |   ]
                        # [---+----+---]
                        # [ML |    | MR]
                        # [---+----+---]
                        # [   | BC |   ]
                        edge_values = (
                            child_values[x + 1][z + 0],  # TC
                            child_values[x + 2][z + 1],  # ML
                            child_values[x + 0][z + 1],  # MR
                            child_values[x + 1][z + 2],  # BC
                        )
                        if all(value is next_value for value in edge_values):
                            biome_values[x][z] = hill_value
                        else:
                            biome_values[x][z] = next_value
                else:
                    biome_values[x][z] = next_value

        if self._debug:
            self._output_debug_data('Hills', x_pos, z_pos, x_width, z_depth, biome_values)

        return biome_values


class SmoothLayer(BaseLayer):

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
                value_ml = child_values[x + 0][z + 1]  # ML
                value_mr = child_values[x + 2][z + 1]  # MR
                value_tc = child_values[x + 1][z + 0]  # TC
                value_bc = child_values[x + 1][z + 2]  # BC
                value_mc = child_values[x + 1][z + 1]  # MC

                if value_ml == value_mr and value_tc == value_bc:
                    self.init_chunk_seed(x_pos + x, z_pos + z)
                    value_mc = value_tc if self.nextInt(2) else value_ml

                else:
                    if value_ml == value_mr:
                        value_mc = value_ml
                    if value_tc == value_bc:
                        value_mc = value_tc

                biome_values[x][z] = value_mc

        if self._debug:
            self._output_debug_data('Smooth', x_pos, z_pos, x_width, z_depth, biome_values)

        return biome_values
