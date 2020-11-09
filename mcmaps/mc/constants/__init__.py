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

''' Constant values used to describe various data in Minecraft. '''

from enum import IntEnum

from . import blocks
from . import world
from .blocks import *
from .world import *

__all__ = [
    *blocks.__all__,
    *world.__all__,
    'DIRECTION',
    'ROTATE_RIGHT', 'ROTATE_LEFT',
    'ROTATE_OPPOSITE', 'OPPOSITE_FACE',
]


class DIRECTION(IntEnum):
    NONE = -1
    SOUTH = 0
    WEST = 1
    NORTH = 2
    EAST = 3


ROTATE_RIGHT = (
    DIRECTION.WEST,
    DIRECTION.NORTH,
    DIRECTION.EAST,
    DIRECTION.SOUTH,
)

ROTATE_LEFT = (
    DIRECTION.EAST,
    DIRECTION.SOUTH,
    DIRECTION.WEST,
    DIRECTION.NORTH,
)

ROTATE_OPPOSITE = (
    DIRECTION.NORTH,
    DIRECTION.EAST,
    DIRECTION.SOUTH,
    DIRECTION.WEST,
)

OPPOSITE_FACE = (
    1, 0, 3, 2, 5, 4,
)
