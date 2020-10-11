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

''' Python3 equivalent of Java's String class methods '''

from ctypes import c_int32

__all__ = ['hashCode']


def hashCode(string):
    '''
        Returns a hash code for this string. The hash code for a `String`
        object is computed as
        ```
        s[0]*31^(n-1) + s[1]*31^(n-2) + ... + s[n-1]
        ```
        using `int` arithmetic, where `s[i]` is the _i_th character of the
        string, `n` is the length of the string, and `^` indicates
        exponentiation. (The hash value of the empty string is zero.)

        @return  a hash code value for this object.
    '''
    h = c_int32()
    for c in string:
        h.value = 31 * h.value + ord(c)
    return h.value
