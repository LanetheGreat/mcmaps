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

''' Island, Beach, and Ocean layer generation. '''

from ._abc import BaseLayer
from mcmaps.mc.constants import BIOME_ID

__all__ = [
    'IslandLayer', 'AddIslandLayer', 'AddMushroomIslandLayer',
    'ShoreLayer',
]


class IslandLayer(BaseLayer):

    def get_area(self, x_pos, z_pos, x_width, z_depth):
        biome_values = [[BIOME_ID.OCEAN] * z_depth for _ in range(x_width)]

        for z in range(z_depth):
            for x in range(x_width):
                self.init_chunk_seed(x_pos + x, z_pos + z)

                if not self.nextInt(10):
                    biome_values[x][z] = BIOME_ID.PLAINS
                else:
                    biome_values[x][z] = BIOME_ID.OCEAN

        if (x_pos > -x_width and x_pos <= 0) and \
           (z_pos > -z_depth and z_pos <= 0):
            biome_values[-x_pos][-z_pos] = BIOME_ID.PLAINS

        if self._debug:
            self._output_debug_data('Island', x_pos, z_pos, x_width, z_depth, biome_values)

        return biome_values


class AddIslandLayer(BaseLayer):

    def get_area(self, x_pos, z_pos, x_width, z_depth):
        biome_values = [[BIOME_ID.OCEAN] * z_depth for _ in range(x_width)]
        child_values = self.child_layer.get_area(
            x_pos - 1, z_pos - 1,
            x_width + 2, z_depth + 2,
        )

        for z in range(z_depth):
            for x in range(x_width):
                self.init_chunk_seed(x_pos + x, z_pos + z)

                # T=Top,  M=Middle, B=Bottom
                # L=Left, C=Center, R=Right
                #
                # [TL |    | TR]
                # [---+----+---]
                # [   | MC |   ]
                # [---+----+---]
                # [BL |    | BR]
                center_value = child_values[x + 1][z + 1]  # MC
                corner_values = (
                    child_values[x + 0][z + 0],  # TL
                    child_values[x + 2][z + 0],  # TR
                    child_values[x + 0][z + 2],  # BL
                    child_values[x + 2][z + 2],  # BR
                )

                if center_value is BIOME_ID.OCEAN and any(
                    value is not BIOME_ID.OCEAN for value in corner_values
                ):
                    corner_probability = 1
                    next_value = BIOME_ID.PLAINS

                    for value in corner_values:
                        if value is not BIOME_ID.OCEAN:
                            if not self.nextInt(corner_probability):
                                next_value = value
                            corner_probability += 1

                    if not self.nextInt(3):
                        biome_values[x][z] = next_value
                    elif next_value is BIOME_ID.PLAINS_ICE:
                        biome_values[x][z] = BIOME_ID.OCEAN_FROZEN
                    else:
                        biome_values[x][z] = BIOME_ID.OCEAN

                elif center_value is not BIOME_ID.OCEAN and BIOME_ID.OCEAN in corner_values:
                    if not self.nextInt(5):
                        if center_value is BIOME_ID.PLAINS_ICE:
                            biome_values[x][z] = BIOME_ID.OCEAN_FROZEN
                        else:
                            biome_values[x][z] = BIOME_ID.OCEAN
                    else:
                        biome_values[x][z] = center_value
                else:
                    biome_values[x][z] = center_value

        if self._debug:
            self._output_debug_data('AddIsland', x_pos, z_pos, x_width, z_depth, biome_values)

        return biome_values


class AddMushroomIslandLayer(BaseLayer):

    def get_area(self, x_pos, z_pos, x_width, z_depth):
        biome_values = [[BIOME_ID.OCEAN] * z_depth for _ in range(x_width)]
        child_values = self.child_layer.get_area(
            x_pos - 1, z_pos - 1,
            x_width + 2, z_depth + 2,
        )

        for z in range(z_depth):
            for x in range(x_width):
                self.init_chunk_seed(x_pos + x, z_pos + z)

                # T=Top,  M=Middle, B=Bottom
                # L=Left, C=Center, R=Right
                #
                # [TL |    | TR]
                # [---+----+---]
                # [   | MC |   ]
                # [---+----+---]
                # [BL |    | BR]
                center_value = child_values[x + 1][z + 1]  # MC
                value_matrix = (
                    child_values[x + 0][z + 0],  # TL
                    child_values[x + 2][z + 0],  # TR
                    child_values[x + 0][z + 2],  # BL
                    child_values[x + 2][z + 2],  # BR
                    center_value,
                )

                if all(value is BIOME_ID.OCEAN for value in value_matrix) and \
                   not self.nextInt(100):
                    biome_values[x][z] = BIOME_ID.MUSHROOM_ISLAND
                else:
                    biome_values[x][z] = center_value

        if self._debug:
            self._output_debug_data('AddMushroomIsland', x_pos, z_pos, x_width, z_depth, biome_values)

        return biome_values


class ShoreLayer(BaseLayer):

    def get_area(self, x_pos, z_pos, x_width, z_depth):
        biome_values = [[BIOME_ID.OCEAN] * z_depth for _ in range(x_width)]
        child_values = self.child_layer.get_area(
            x_pos - 1, z_pos - 1,
            x_width + 2, z_depth + 2,
        )

        for z in range(z_depth):
            for x in range(x_width):
                self.init_chunk_seed(x_pos + x, z_pos + z)

                # T=Top,  M=Middle, B=Bottom
                # L=Left, C=Center, R=Right
                #
                # [   | TC |   ]
                # [---+----+---]
                # [ML | MC | MR]
                # [---+----+---]
                # [   | BC |   ]
                center_value = child_values[x + 1][z + 1]  # MC
                edge_values = (
                    child_values[x + 1][z + 0],  # TC
                    child_values[x + 2][z + 1],  # ML
                    child_values[x + 0][z + 1],  # MR
                    child_values[x + 1][z + 2],  # BC
                )

                if center_value is BIOME_ID.MUSHROOM_ISLAND:
                    if BIOME_ID.OCEAN not in edge_values:
                        biome_values[x][z] = center_value
                    else:
                        biome_values[x][z] = BIOME_ID.MUSHROOM_BEACH

                elif center_value not in (
                    BIOME_ID.OCEAN, BIOME_ID.RIVER,
                    BIOME_ID.SWAMP, BIOME_ID.HILLS_EXTREME,
                ):
                    if BIOME_ID.OCEAN not in edge_values:
                        biome_values[x][z] = center_value
                    else:
                        biome_values[x][z] = BIOME_ID.BEACH

                elif center_value is BIOME_ID.HILLS_EXTREME:
                    if all(value is BIOME_ID.HILLS_EXTREME for value in edge_values):
                        biome_values[x][z] = center_value
                    else:
                        biome_values[x][z] = BIOME_ID.HILLS_EXTREME_EDGE

                else:
                    biome_values[x][z] = center_value

        if self._debug:
            self._output_debug_data('Beach', x_pos, z_pos, x_width, z_depth, biome_values)

        return biome_values
