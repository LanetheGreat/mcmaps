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

''' Base classes for biomes and layer generation. '''

from abc import ABC, abstractmethod
from collections import OrderedDict
from ctypes import c_int32, c_int64

__all__ = [
    'BaseLayer',
]


class BaseLayer(ABC):
    __slots__ = ('child_layer', 'world_seed', 'chunk_seed', 'layer_seed', '_debug')

    def __init__(self, layer_seed, child=None, debug=None):
        self._debug = debug
        self.child_layer = child
        self.world_seed = c_int64(0)
        self.chunk_seed = c_int64(0)
        self.layer_seed = c_int64(layer_seed)

        self.layer_seed.value *= self.layer_seed.value * 6364136223846793005 + 1442695040888963407
        self.layer_seed.value += layer_seed

        self.layer_seed.value *= self.layer_seed.value * 6364136223846793005 + 1442695040888963407
        self.layer_seed.value += layer_seed

        self.layer_seed.value *= self.layer_seed.value * 6364136223846793005 + 1442695040888963407
        self.layer_seed.value += layer_seed

    def __repr__(self):
        values = (
            ('world seed', self.world_seed.value),
            ('chunk seed', self.chunk_seed.value),
            ('layer seed', self.layer_seed.value),
            ('child', self.child_layer),
        )

        return '%s(%s)' % (
            self.__class__.__name__,
            ', '.join('%s=%s' % value for value in values),
        )

    def init_world_seed(self, world_seed):
        self.world_seed.value = world_seed
        layer_seed = self.layer_seed.value

        if self.child_layer:
            self.child_layer.init_world_seed(world_seed)

        self.world_seed.value *= self.world_seed.value * 6364136223846793005 + 1442695040888963407
        self.world_seed.value += layer_seed

        self.world_seed.value *= self.world_seed.value * 6364136223846793005 + 1442695040888963407
        self.world_seed.value += layer_seed

        self.world_seed.value *= self.world_seed.value * 6364136223846793005 + 1442695040888963407
        self.world_seed.value += layer_seed

    def init_chunk_seed(self, chunkX, chunkZ):
        self.chunk_seed.value = self.world_seed.value

        self.chunk_seed.value *= self.chunk_seed.value * 6364136223846793005 + 1442695040888963407
        self.chunk_seed.value += chunkX

        self.chunk_seed.value *= self.chunk_seed.value * 6364136223846793005 + 1442695040888963407
        self.chunk_seed.value += chunkZ

        self.chunk_seed.value *= self.chunk_seed.value * 6364136223846793005 + 1442695040888963407
        self.chunk_seed.value += chunkX

        self.chunk_seed.value *= self.chunk_seed.value * 6364136223846793005 + 1442695040888963407
        self.chunk_seed.value += chunkZ

    def nextInt(self, bound):
        next_value = c_int32((self.chunk_seed.value >> 24) % bound)

        self.chunk_seed.value *= self.chunk_seed.value * 6364136223846793005 + 1442695040888963407
        self.chunk_seed.value += self.world_seed.value

        return next_value.value

    def _output_debug_data(self, name, x_pos, z_pos, x_width, z_depth, area):
        ''' Used during implementation testing with an SAX XML writer in _debug. '''
        if not self._debug:
            return

        debug = self._debug
        debug.startElement('layer', OrderedDict((
            ('type', name),
            ('x', str(x_pos)),
            ('z', str(z_pos)),
            ('width', str(x_width)),
            ('depth', str(z_depth)),
            ('world_seed', str(self.world_seed.value)),
            ('layer_seed', str(self.layer_seed.value)),
            ('chunk_seed', str(self.chunk_seed.value)),
        )))

        for z in range(z_depth):
            debug.startElement('values', {})
            biomes = map(int, (area[x][z] for x in range(x_width)))
            debug.characters(' '.join(map(str, biomes)))
            debug.endElement('values')

        debug.endElement('layer')

    @abstractmethod
    def get_area(self, x_pos, z_pos, x_width, z_depth):
        pass
