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

''' Constants in World and Biome generation. '''

from collections import namedtuple
from enum import IntEnum

from .blocks import BLOCK_ID

__all__ = ['BIOME_ID', 'WORLD_TYPE', 'Color']


Color = namedtuple('Color', ('r', 'g', 'b'))


class BIOME_ID(IntEnum):

    def __new__(
            cls, value,
            min_height=0.1, max_height=0.3,
            temperature=0.5, rainfall=0.5,
            color=Color(0, 0, 0),
            top_block=BLOCK_ID.GRASS.block,  # @UndefinedVariable
            fill_block=BLOCK_ID.DIRT.block,  # @UndefinedVariable
    ):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj._minheight_ = min_height
        obj._maxheight_ = max_height
        obj._temperature_ = temperature
        obj._rainfall_ = rainfall
        obj._color_ = color
        obj._topblock_ = top_block
        obj._fillblock_ = fill_block
        return obj

    @property
    def min_height(self):
        return self._minheight_

    @property
    def max_height(self):
        return self._maxheight_

    @property
    def temperature(self):
        return self._temperature_

    @property
    def rainfall(self):
        return self._rainfall_

    @property
    def color(self):
        return self._color_

    @property
    def top_block(self):
        return self._topblock_

    @property
    def fill_block(self):
        return self._fillblock_

    # Values (Biome ID, Min Height, Max Height, Temperature, Rainfall, Color, Top Block, Filler Block)
    NONE                = -1
    OCEAN               = 0,  -1.0, 0.4, 0.5,  0.5, Color(0,     0, 112)
    OCEAN_FROZEN        = 10, -1.0, 0.5, 0.0,  0.5, Color(144, 144, 160)
    PLAINS              = 1,  0.1,  0.3, 0.8,  0.4, Color(141, 179,  96)
    PLAINS_ICE          = 12, 0.1,  0.3, 0.0,  0.5, Color(255, 255, 255)
    DESERT              = 2,  0.1,  0.2, 2.0,  0.0, Color(250, 148,  24), BLOCK_ID.SAND.block, BLOCK_ID.SAND.block  # @UndefinedVariable
    HILLS_EXTREME       = 3,  0.3,  1.5, 0.2,  0.3, Color(96,   96,  96)
    HILLS_EXTREME_ICE   = 13, 0.3,  1.3, 0.0,  0.5, Color(160, 160, 160)
    HILLS_EXTREME_EDGE  = 20, 0.2,  0.8, 0.2,  0.3, Color(114, 120, 154)
    HILLS_DESERT        = 17, 0.3,  0.8, 2.0,  0.0, Color(210,  95,  18), BLOCK_ID.SAND.block, BLOCK_ID.SAND.block  # @UndefinedVariable
    HILLS_FOREST        = 18, 0.3,  0.7, 0.7,  0.8, Color(34,   85,  28)
    HILLS_TAIGA         = 19, 0.3,  0.8, 0.05, 0.8, Color(22,   57,  51)
    HILLS_JUNGLE        = 22, 1.8,  0.5, 1.2,  0.9, Color(44,   66,   5)
    FOREST              = 4,  0.1,  0.3, 0.7,  0.8, Color(5,   102,  33)
    TAIGA               = 5,  0.1,  0.4, 0.05, 0.8, Color(11,  102,  89)
    SWAMP               = 6,  -0.2, 0.1, 0.8,  0.9, Color(7,   249, 178)
    RIVER               = 7,  -0.5, 0.0, 0.5,  0.5, Color(0,     0, 255)
    RIVER_FROZEN        = 11, -0.5, 0.0, 0.0,  0.5, Color(160, 160, 255)
    HELL                = 8,  0.1,  0.3, 2.0,  0.0, Color(255,   0,   0)
    SKY                 = 9,  0.1,  0.3, 0.5,  0.5, Color(128, 128, 255)
    MUSHROOM_ISLAND     = 14, 0.2,  1.0, 0.9,  1.0, Color(255,   0, 255), BLOCK_ID.MYCELIUM.block  # @UndefinedVariable
    MUSHROOM_BEACH      = 15, -1.0, 0.1, 0.9,  1.0, Color(160,   0, 255), BLOCK_ID.MYCELIUM.block  # @UndefinedVariable
    BEACH               = 16, 0.0,  0.1, 0.8,  0.4, Color(250, 222,  85), BLOCK_ID.SAND.block, BLOCK_ID.SAND.block  # @UndefinedVariable
    JUNGLE              = 21, 0.2,  0.4, 1.2,  0.9, Color(83,  123,   9)


class WORLD_TYPE(IntEnum):
    DEFAULT = 0
    FLAT = 1
    LARGE_BIOME = 2
    DEFAULT_1_1 = 8
