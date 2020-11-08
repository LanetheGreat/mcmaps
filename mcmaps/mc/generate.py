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

''' Classes used for map generation '''

from math import sqrt

from mcmaps.java.random import Random
from mcmaps.mc.noise import SimplexNoiseGenerator

__all__ = ['ChunkGenerator']


class ChunkGenerator:
    __slots__ = ('rand', 'noise_generators')

    # Gaussian kernel matrix for smoothing block heights between biome boundaries.
    parabolic_values = [
        [
            10.0 / sqrt(x * x + z * z + 0.2)
            for x in range(-2, 3)
        ]
        for z in range(-2, 3)
    ]

    def __init__(self, seed):
        self.rand = Random(seed)
        self.noise_generators = [
            SimplexNoiseGenerator(self.rand, level)
            for level in (16, 16, 8, 4, 10, 16)
        ]
