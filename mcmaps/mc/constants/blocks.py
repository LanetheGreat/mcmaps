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

''' Constants and Functions used with Block data. '''

from collections import namedtuple
from enum import IntEnum

__all__ = ['Block', 'BLOCK_ID']

Block = namedtuple('Block', ('id', 'metadata'))


class BLOCK_ID(IntEnum):

    def __new__(cls, value, opaque=True, liquid=False, directional=False):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj._opaque_ = opaque
        obj._liquid_ = liquid
        obj._directional_ = directional
        obj._block_ = Block(obj, 0)
        return obj

    @property
    def opaque(self):
        return self._opaque

    @property
    def liquid(self):
        return self._liquid_

    @property
    def block(self):
        return self._block_

    @property
    def directional(self):
        return self._directional_

    def withmeta(self, meta=0):
        if self == 0 and meta != 0:
            raise ValueError('Air blocks cannot have metadata.')
        return Block(self, meta)

    AIR = 0, False
    STONE = 1
    STONE_BRICK = 98
    STONE_WHITE = 121
    GRASS = 2
    DIRT = 3
    DIRT_TILLED = 60
    COBBLESTONE = 4
    COBBLESTONE_MOSSY = 48
    PLANKS = 5
    SAPLING = 6, False
    BEDROCK = 7
    WATER_MOVING = 8, False, True
    WATER_STILL = 9, False, True
    LAVA_MOVING = 10, False, True
    LAVA_STILL = 11, False, True
    SAND = 12
    GRAVEL = 13
    ORE_GOLD = 14
    ORE_IRON = 15
    ORE_COAL = 16
    ORE_DIAMOND = 56
    ORE_LAPIS = 21
    ORE_REDSTONE = 73
    ORE_REDSTONE_GLOWING = 74
    ORE_EMERALD = 129
    ORE_NETHER_QUARTZ = 153
    WOOD = 17
    LEAVES = 18, False
    SPONGE = 19
    GLASS = 20, False
    GLASS_PANE = 102, False
    BLOCK_LAPIS = 22
    BLOCK_GOLD = 41
    BLOCK_IRON = 42
    BLOCK_DIAMOND = 57
    BLOCK_SNOW = 80
    BLOCK_CLAY = 82
    BLOCK_EMERALD = 133
    BLOCK_REDSTONE = 152
    BLOCK_NETHER_QUARTZ = 155
    BLOCK_COAL = 173
    DISPENSER = 23
    SANDSTONE = 24
    MUSIC = 25
    BED = 26, True, False, True
    RAIL_POWERED = 27, False
    RAIL_DETECTOR = 28, False
    RAIL_ACTIVATOR = 157, False
    RAIL = 66, False
    PISTON_STICKY = 29
    PISTON_BASE = 33
    PISTON_EXT = 34
    PISTON_MOVING = 36
    WEB = 30, False
    TALL_GRASS = 31, False
    DEAD_BUSH = 32, False
    WOOL = 35
    PLANT_YELLOW = 37, False
    PLANT_RED = 38, False
    MUSHROOM_BROWN = 39, False
    MUSHROOM_RED = 40, False
    DBL_SLAB_STONE = 43
    DBL_SLAB_WOOD = 125
    SLAB_STONE = 44
    SLAB_WOOD = 126
    BRICK = 45
    TNT = 46
    BOOKSHELF = 47
    OBSIDIAN = 49
    TORCH_WOOD = 50, False
    TORCH_REDSTONE_IDLE = 75, False
    TORCH_REDSTONE_ACTIVE = 76, False
    FIRE = 51, False
    MOB_SPAWNER = 52, False
    STAIRS_WOOD_OAK = 53
    STAIRS_COBBLESTONE = 67
    STAIRS_BRICK = 108
    STAIRS_STONE_BRICK = 109
    STAIRS_NETHER_BRICK = 114
    STAIRS_SANDSTONE = 128
    STAIRS_WOOD_SPRUCE = 134
    STAIRS_WOOD_BIRCH = 135
    STAIRS_WOOD_JUNGLE = 136
    STAIRS_NETHER_QUARTZ = 156
    CHEST = 54
    CHEST_LOCKED = 95
    CHEST_ENDER = 130
    CHEST_TRAPPED = 146
    REDSTONE_WIRE = 55, False
    REDSTONE_LAMP_IDLE = 123
    REDSTONE_LAMP_ACTIVE = 124
    WORKBENCH = 58
    CROPS = 59, False
    FURNACE_IDLE = 61
    FURNACE_BURNING = 62
    SIGN_POST = 63, False
    SIGN_WALL = 68, False
    DOOR_WOOD = 64
    DOOR_IRON = 71, False
    LADDER = 65, False
    LEVER = 69, False
    PRESSURE_PLATE_STONE = 70
    PRESSURE_PLATE_WOOD = 72
    PRESSURE_PLATE_GOLD = 147
    PRESSURE_PLATE_IRON = 148
    BUTTON_STONE = 77, False
    BUTTON_WOOD = 143, False
    SNOW = 78
    ICE = 79
    CACTUS = 81
    REED = 83, False
    JUKEBOX = 84
    FENCE_WOOD = 85, False
    FENCE_IRON = 101, False
    FENCE_GATE = 107, False, False, True
    FENCE_NETHER = 113, False
    PUMPKIN = 86, True, False, True
    PUMPKIN_LANTERN = 91
    PUMPKIN_STEM = 104, False
    MELON = 103
    MELON_STEM = 105, False
    NETHERRACK = 87
    SOUL_SAND = 88
    GLOW_STONE = 89
    PORTAL = 90
    CAKE = 92
    REPEATER_IDLE = 93, True, False, True
    REPEATER_ACTIVE = 94, True, False, True
    TRAPDOOR = 96, False
    SILVERFISH = 97
    MUSHROOM_CAP_BROWN = 99
    MUSHROOM_CAP_RED = 100
    VINE = 106, False
    MYCELIUM = 110
    LILYPAD = 111, False
    NETHER_BRICK = 112
    NETHER_WART = 115, False
    ENCHANTMENT_TABLE = 116
    BREWING_STAND = 117, False
    CAULDRON = 118
    END_PORTAL = 119
    END_PORTAL_FRAME = 120
    DRAGON_EGG = 122, False
    COCOA_PLANT = 127, False, False, True
    TRIP_WIRE_SOURCE = 131, False
    TRIP_WIRE = 132, False
    COMMAND_BLOCK = 137
    BEACON = 138
    WALL_COBBLESTONE = 139, False
    FLOWER_POT = 140, False
    CARROT = 141, False
    POTATO = 142, False
    SKULL = 144, False
    ANVIL = 145, False
    COMPARATOR_IDLE = 149, True, False, True
    COMPARATOR_ACTIVE = 150, True, False, True
    DAYLIGHT_SENSOR = 151
    HOPPER = 154
    DROPPER = 158, False
    CLAY_STAINED = 159
    CLAY_HARDENED = 172
    HAY = 170
    CARPET = 171
