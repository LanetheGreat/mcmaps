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

''' Layers used for zooming during biome generation. '''

from abc import abstractmethod

from ._abc import BaseLayer
from mcmaps.mc.constants import BIOME_ID

__all__ = [
    'FuzzyZoomLayer', 'VoronoiZoomLayer', 'ZoomLayer',
]


class _BaseZoomLayer(BaseLayer):

    def get_area(self, x_pos, z_pos, x_width, z_depth):
        child_x_pos = x_pos >> 1
        child_z_pos = z_pos >> 1
        child_x_width = (x_width >> 1) + 3
        child_z_depth = (z_depth >> 1) + 3
        zoom_z_depth = child_z_depth << 1

        biome_values = [[BIOME_ID.OCEAN] * z_depth for _ in range(x_width)]
        zoom_values = [[BIOME_ID.OCEAN] * zoom_z_depth for _ in range(child_x_width << 1)]
        child_values = self.child_layer.get_area(
            child_x_pos, child_z_pos, child_x_width, child_z_depth,
        )

        for z in range(child_z_depth - 1):
            # T=Top,  B=Bottom
            # L=Left, R=Right
            #
            # [TL | TR]
            # [---+---]
            # [BL | BR]

            # Take each row from the child and place it every second row in the zoomed values.
            z2 = z << 1

            # Values are accumulated left to right along the X axis.
            top_accl = child_values[0][z + 0]  # Child TL
            bot_accl = child_values[0][z + 1]  # Child BL

            for x in range(child_x_width - 1):
                self.init_chunk_seed(child_x_pos + x << 1, child_z_pos + z << 1)

                top_next = child_values[x + 1][z + 0]  # Child TR
                bot_next = child_values[x + 1][z + 1]  # Child BR

                # Take each column from the child and place it every second column in the zoomed values.
                x2 = x << 1

                zoom_values[x2 + 0][z2 + 0] = top_accl                         # Zoom TL
                zoom_values[x2 + 0][z2 + 1] = self.choose(top_accl, bot_accl)  # Zoom BL
                zoom_values[x2 + 1][z2 + 0] = self.choose(top_accl, top_next)  # Zoom TR
                zoom_values[x2 + 1][z2 + 1] = self.diagonal_func(              # Zoom BR
                    top_accl, top_next, bot_accl, bot_next,
                )

                top_accl = top_next
                bot_accl = bot_next

        # Extract the inner square, a subset of the zoomed values.
        x_offset = x_pos & 1
        z_offset = z_pos & 1
        for z in range(z_depth):
            for x in range(x_width):
                biome_values[x][z] = zoom_values[x + x_offset][z + z_offset]

        return biome_values

    def choose(self, *args):
        return args[self.nextInt(len(args))]

    @abstractmethod
    def diagonal_func(self, value_tl, value_tr, value_bl, value_br):
        ''' Calculates the result of using all 4 corner values for BR's values. '''


class FuzzyZoomLayer(_BaseZoomLayer):

    diagonal_func = _BaseZoomLayer.choose

    def get_area(self, x_pos, z_pos, x_width, z_depth):
        biome_values = super().get_area(x_pos, z_pos, x_width, z_depth)

        if self._debug:
            self._output_debug_data('FuzzyZoom', x_pos, z_pos, x_width, z_depth, biome_values)

        return biome_values


class ZoomLayer(_BaseZoomLayer):

    @classmethod
    def zoom(cls, layer_seed, child, zoom_count, _debug=None):
        layer = child

        for zoom in range(zoom_count):
            layer = cls(layer_seed + zoom, layer, _debug=_debug)

        return layer

    def get_area(self, x_pos, z_pos, x_width, z_depth):
        biome_values = super().get_area(x_pos, z_pos, x_width, z_depth)

        if self._debug:
            self._output_debug_data('Zoom', x_pos, z_pos, x_width, z_depth, biome_values)

        return biome_values

    def diagonal_func(self, value_tl, value_tr, value_bl, value_br):
        if value_tr == value_bl and value_bl == value_br:
            return value_tr
        if value_tl == value_tr and value_tl == value_bl:
            return value_tl
        if value_tl == value_tr and value_tl == value_br:
            return value_tl
        if value_tl == value_bl and value_tl == value_br:
            return value_tl
        if value_tl == value_tr and value_bl != value_br:
            return value_tl
        if value_tl == value_bl and value_tr != value_br:
            return value_tl
        if value_tl == value_br and value_tr != value_bl:
            return value_tl
        if value_tr == value_tl and value_bl != value_br:
            return value_tr
        if value_tr == value_bl and value_tl != value_br:
            return value_tr
        if value_tr == value_br and value_tl != value_bl:
            return value_tr
        if value_bl == value_tl and value_tr != value_br:
            return value_bl
        if value_bl == value_tr and value_tl != value_br:
            return value_bl
        if value_bl == value_br and value_tl != value_tr:
            return value_bl
        if value_br == value_tl and value_tr != value_bl:
            return value_bl
        if value_br == value_tr and value_tl != value_bl:
            return value_bl
        if value_br == value_bl and value_tl != value_tr:
            return value_bl

        return self.choose(value_tl, value_tr, value_bl, value_br)


class VoronoiZoomLayer(BaseLayer):

    def get_area(self, x_pos, z_pos, x_width, z_depth):
        x_pos -= 2
        z_pos -= 2
        child_x_pos = x_pos >> 2
        child_z_pos = z_pos >> 2
        child_x_width = (x_width >> 2) + 3
        child_z_depth = (z_depth >> 2) + 3
        zoom_z_depth = child_z_depth << 2

        biome_values = [[BIOME_ID.OCEAN] * z_depth for _ in range(x_width)]
        zoom_values = [[BIOME_ID.OCEAN] * zoom_z_depth for _ in range(child_x_width << 2)]
        child_values = self.child_layer.get_area(
            child_x_pos, child_z_pos, child_x_width, child_z_depth,
        )

        for z in range(child_z_depth - 1):
            # T=Top,  B=Bottom
            # L=Left, R=Right
            #
            # [TL | TR]
            # [---+---]
            # [BL | BR]

            # Take each pixel in a row from the child and stretch it across a 4x4 cell.
            z2 = z << 2

            # Values are accumulated left to right along the X axis.
            top_accl = child_values[0][z + 0]  # Child TL
            bot_accl = child_values[0][z + 1]  # Child BL

            for x in range(child_x_width - 1):
                # Random TL Corner X/Z
                self.init_chunk_seed(child_x_pos + x + 0 << 2, child_z_pos + z + 0 << 2)
                corner_tl_x = self.nextDouble(1024) * 3.6
                corner_tl_z = self.nextDouble(1024) * 3.6

                # Random TR Corner X/Z
                self.init_chunk_seed(child_x_pos + x + 1 << 2, child_z_pos + z + 0 << 2)
                corner_tr_x = self.nextDouble(1024) * 3.6 + 4.0
                corner_tr_z = self.nextDouble(1024) * 3.6

                # Random BL Corner X/Z
                self.init_chunk_seed(child_x_pos + x + 0 << 2, child_z_pos + z + 1 << 2)
                corner_bl_x = self.nextDouble(1024) * 3.6
                corner_bl_z = self.nextDouble(1024) * 3.6 + 4.0

                # Random BR Corner X/Z
                self.init_chunk_seed(child_x_pos + x + 1 << 2, child_z_pos + z + 1 << 2)
                corner_br_x = self.nextDouble(1024) * 3.6 + 4.0
                corner_br_z = self.nextDouble(1024) * 3.6 + 4.0

                top_next = child_values[x + 1][z + 0]  # Child TR
                bot_next = child_values[x + 1][z + 1]  # Child BR

                # Take each pixel in a column from the child and stretch it across a 4x4 cell.
                x2 = x << 2

                for cell_z in range(4):
                    for cell_x in range(4):
                        # Calculate pseudo-distances from each generated corner.
                        dist_tl = (cell_z-corner_tl_z) * (cell_z-corner_tl_z) + (cell_x-corner_tl_x) * (cell_x-corner_tl_x)
                        dist_tr = (cell_z-corner_tr_z) * (cell_z-corner_tr_z) + (cell_x-corner_tr_x) * (cell_x-corner_tr_x)
                        dist_bl = (cell_z-corner_bl_z) * (cell_z-corner_bl_z) + (cell_x-corner_bl_x) * (cell_x-corner_bl_x)
                        dist_br = (cell_z-corner_br_z) * (cell_z-corner_br_z) + (cell_x-corner_br_x) * (cell_x-corner_br_x)

                        if all(dist_tl < dist for dist in (dist_tr, dist_bl, dist_br)):
                            # Use the TL corner if it's closest.
                            zoom_values[x2 + cell_x][z2 + cell_z] = top_accl
                        elif all(dist_tr < dist for dist in (dist_tl, dist_bl, dist_br)):
                            # Use the TR corner if it's closest.
                            zoom_values[x2 + cell_x][z2 + cell_z] = top_next
                        elif all(dist_bl < dist for dist in (dist_tl, dist_tr, dist_br)):
                            # Use the BL corner if it's closest.
                            zoom_values[x2 + cell_x][z2 + cell_z] = bot_accl
                        else:
                            # Use the BR corner if all others fail.
                            zoom_values[x2 + cell_x][z2 + cell_z] = bot_next

                top_accl = top_next
                bot_accl = bot_next

        # Extract the inner square, a subset of the zoomed values.
        x_offset = x_pos & 3
        z_offset = z_pos & 3
        for z in range(z_depth):
            for x in range(x_width):
                biome_values[x][z] = zoom_values[x + x_offset][z + z_offset]

        if self._debug:
            self._output_debug_data('VoronoiZoom', x_pos, z_pos, x_width, z_depth, biome_values)

        return biome_values

    def nextDouble(self, precision):
        return self.nextInt(precision) / precision - 0.5
