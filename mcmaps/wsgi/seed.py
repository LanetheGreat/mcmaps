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

''' Calculates a numeric seed, given either a 64-bit number or text string '''

from urllib.parse import parse_qs

from mcmaps.java.string import hashCode
from mcmaps.util.misc import SLONG_RANGE

__all__ = ('application',)


def application(env, start_response):
    query = parse_qs(env['QUERY_STRING'])
    seed_text = query.get('seed', ('',))[0] or 0

    try:
        seed = int(seed_text)
        if seed not in SLONG_RANGE:
            raise ValueError
    except ValueError:
        seed = hashCode(seed_text)

    start_response('200 OK', [])
    return [str(seed).encode()]
