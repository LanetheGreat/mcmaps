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

''' Common functionality used by MC Maps WSGI script endpoints '''

from os import makedirs
from os.path import join


__all__ = ['ensure_world_paths']


def _ensure_dim_folders(world_path, dim):
    # Create the blocks, layers, and biomes maps folders
    makedirs(join(world_path, dim, 'blocks'), exist_ok=True)
    makedirs(join(world_path, dim, 'layers'), exist_ok=True)
    makedirs(join(world_path, dim, 'biomes'), exist_ok=True)


def ensure_world_paths(path):
    # Create the seeds project folder
    makedirs(path, exist_ok=True)

    # Make dimensions for Overworld, Nether, and the End.
    _ensure_dim_folders(path, 'DIM0')
    _ensure_dim_folders(path, 'DIM-1')
    _ensure_dim_folders(path, 'DIM1')
