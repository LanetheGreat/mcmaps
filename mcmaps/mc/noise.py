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

''' Minecraft implementation of Perlin Noise generation '''

__all__ = [
    'BaseNoiseGenerator',
    'ImprovedNoiseGenerator',
    'SimplexNoiseGenerator',
]

from math import floor
from mcmaps.java.random import Random


class BaseNoiseGenerator:
    pass


class ImprovedNoiseGenerator(BaseNoiseGenerator):

    __slots__ = (
        'permutations',
        'x', 'y', 'z',
    )

    def __init__(self, random=None):
        if random is None:
            random = Random()

        self.x = random.nextDouble() * 256.0
        self.y = random.nextDouble() * 256.0
        self.z = random.nextDouble() * 256.0
        self.permutations = list(range(512))

        for index in range(256):
            swap_index = random.nextInt(256 - index) + index
            self.permutations[index], self.permutations[index + 256], self.permutations[swap_index] = \
                self.permutations[swap_index], self.permutations[swap_index], self.permutations[index]

    # Linear interpolate
    @staticmethod
    def lerp(weight, src, dst):
        return src + weight * (dst - src)

    @staticmethod
    def grad2D(hash_, x, z):
        h = hash_ & 15
        u = (1.0 - ((h & 8) >> 3)) * x
        v = 0.0 if h < 4 else (x if h in (12, 14) else z)
        return (-u if h & 1 else u) + (-v if h & 2 else v)

    @staticmethod
    def grad3D(hash_, x, y, z):
        h = hash_ & 15
        u = x if h < 8 else y
        v = y if h < 4 else (x if h in (12, 14) else z)
        return (-u if h & 1 else u) + (-v if h & 2 else v)

    @staticmethod
    def fade(t):
        return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)

    def generate_noise(self, xOffset, yOffset, zOffset, xSize, ySize, zSize, xScale, yScale, zScale, noise_scale, noise=None):
        if noise is None:
            noise = [0.0] * (xSize * ySize * zSize)

        noise_index = 0
        scale_inverse = 1.0 / noise_scale

        if ySize == 1:
            for x in range(xSize):
                xPos = xOffset + x * xScale + self.x
                xPosInt = int(xPos)

                if xPos < xPosInt:
                    xPosInt -= 1

                xIndex = xPosInt & 255
                xPos -= xPosInt
                xWeight = self.fade(xPos)

                for z in range(zSize):
                    zPos = zOffset + z * zScale + self.z
                    zPosInt = int(zPos)

                    if zPos < zPosInt:
                        zPosInt -= 1

                    zIndex = zPosInt & 255
                    zPos -= zPosInt
                    zWeight = self.fade(zPos)

                    hashIndex1 = self.permutations[self.permutations[xIndex]]     + zIndex
                    hashIndex2 = self.permutations[self.permutations[xIndex + 1]] + zIndex
                    srcLerp = self.lerp(xWeight, self.grad2D(self.permutations[hashIndex1], xPos, zPos), self.grad3D(self.permutations[hashIndex2], xPos - 1.0, 0.0, zPos))
                    dstLerp = self.lerp(xWeight, self.grad3D(self.permutations[hashIndex1 + 1], xPos, 0.0, zPos - 1.0), self.grad3D(self.permutations[hashIndex2 + 1], xPos - 1.0, 0.0, zPos - 1.0))
                    noise[noise_index] += self.lerp(zWeight, srcLerp, dstLerp) * scale_inverse
                    noise_index += 1
        else:
            prevYIndex = -1
            frontTR2TL = 0.0
            frontBR2BL = 0.0
            backTR2TL = 0.0
            backBR2BL = 0.0

            for x in range(xSize):
                xPos = xOffset + x * xScale + self.x
                xPosInt = int(xPos)

                if (xPos < xPosInt):
                    xPosInt -= 1

                xIndex = xPosInt & 255
                xPos -= xPosInt
                xWeight = self.fade(xPos)

                for z in range(zSize):
                    zPos = zOffset + z * zScale + self.z
                    zPosInt = int(zPos)

                    if (zPos < zPosInt):
                        zPosInt -= 1

                    zIndex = zPosInt & 255
                    zPos -= zPosInt
                    zWeight = self.fade(zPos)

                    for y in range(ySize):
                        yPos = yOffset + y * yScale + self.y
                        yPosInt = int(yPos)

                        if (yPos < yPosInt):
                            yPosInt -= 1

                        yIndex = yPosInt & 255
                        yPos -= yPosInt
                        yWeight = self.fade(yPos)

                        if (y == 0 or yIndex != prevYIndex):
                            prevYIndex = yIndex
                            rightIndex  = self.permutations[xIndex]         + yIndex  # Index to right corner indexes
                            trHashIndex = self.permutations[rightIndex]     + zIndex  # Front Top Right / Back Top Right
                            brHashIndex = self.permutations[rightIndex + 1] + zIndex  # Front Bottom Right / Back Bottom Right
                            leftIndex   = self.permutations[xIndex + 1]     + yIndex  # Index to left corner indexes
                            tlHashIndex = self.permutations[leftIndex]      + zIndex  # Front Top Left / Back Top Left
                            blHashIndex = self.permutations[leftIndex + 1]  + zIndex  # Front Bottom Left / Back Bottom Left
                            frontTR2TL = self.lerp(xWeight, self.grad(self.permutations[trHashIndex], xPos, yPos, zPos), self.grad(self.permutations[tlHashIndex], xPos - 1.0, yPos, zPos))
                            frontBR2BL = self.lerp(xWeight, self.grad(self.permutations[brHashIndex], xPos, yPos - 1.0, zPos), self.grad(self.permutations[blHashIndex], xPos - 1.0, yPos - 1.0, zPos))
                            backTR2TL = self.lerp(xWeight, self.grad(self.permutations[trHashIndex + 1], xPos, yPos, zPos - 1.0), self.grad(self.permutations[tlHashIndex + 1], xPos - 1.0, yPos, zPos - 1.0))
                            backBR2BL = self.lerp(xWeight, self.grad(self.permutations[brHashIndex + 1], xPos, yPos - 1.0, zPos - 1.0), self.grad(self.permutations[blHashIndex + 1], xPos - 1.0, yPos - 1.0, zPos - 1.0))

                        noise_lerp = self.lerp(zWeight, self.lerp(yWeight, frontTR2TL, frontBR2BL), self.lerp(yWeight, backTR2TL, backBR2BL))
                        noise[noise_index] += noise_lerp * scale_inverse
                        noise_index += 1
        return noise


class SimplexNoiseGenerator(BaseNoiseGenerator):

    __slots__ = ('level_count', 'noise_levels')

    def __init__(self, random, level_count):
        self.level_count = level_count
        self.noise_levels = [
            ImprovedNoiseGenerator(random) for _ in range(level_count)
        ]

    def generate_noise_levels(self, xOffset, yOffset, zOffset, xSize, ySize, zSize, xScale, yScale, zScale, noise=None):
        if noise is None:
            noise = [0.0] * (xSize * ySize * zSize)

        noise_scale = 1.0

        for level in self.noise_levels:
            levelXOffset = xOffset * noise_scale * xScale
            levelYOffset = yOffset * noise_scale * yScale
            levelZOffset = zOffset * noise_scale * zScale

            xInt = floor(levelXOffset)
            zInt = floor(levelZOffset)

            levelXOffset = levelXOffset - xInt + (xInt % 16777216)
            levelZOffset = levelZOffset - zInt + (zInt % 16777216)

            level.generate_noise(
                levelXOffset, levelYOffset, levelZOffset,
                xSize, ySize, zSize,
                xScale * noise_scale, yScale * noise_scale, zScale * noise_scale,
                noise_scale,
                noise,
            )

            noise_scale /= 2.0

        return noise

    def generate_noise_levels_XZ(self, xOffset, zOffset, xSize, zSize, xScale, zScale, noise=None):
        return self.generateNoiseOctaves(xOffset, 10, zOffset, xSize, 1, zSize, xScale, 1.0, zScale, noise)
