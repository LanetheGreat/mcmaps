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

'''
Tests for the mcmaps.java.random module.

Meant for use with py.test.
Write each test as a function named test_<something>.
Read more here: http://pytest.org/
'''

from mcmaps.java.random import Random


def test_next():
    r = Random(seed=0)
    assert r.next(8)  == 187
    assert r.next(16) == 54489
    assert r.next(24) == 4035531
    assert r.next(32) == 2604232894
    assert r.next(40) == 700847879818
    assert r.next(48) == 86990003003491


def test_nextBytes():
    test_bytes = bytearray(32)
    expected_bytes = bytes([
        96, 180, 32, 187, 56, 81, 217, 212,
        122, 203, 147, 61, 190, 112, 57, 155,
        246, 201, 45, 163, 58, 240, 29, 79,
        183, 112, 233, 140, 3, 37, 244, 29,
    ])

    r = Random(seed=0)
    r.nextBytes(test_bytes)
    assert test_bytes == expected_bytes


def test_nextInt():
    r = Random(seed=0)
    assert r.nextInt(2 ** 8) == 187
    assert r.nextInt(2 ** 16) == 54489
    assert r.nextInt(2 ** 24) == 4035531
    assert r.nextInt() == 2604232894


def test_nextLong():
    r = Random(seed=0)
    assert r.nextLong(2 ** 8) == 56
    assert r.nextLong(2 ** 16) == 28862
    assert r.nextLong(2 ** 24) == 1962042
    assert r.nextLong(2 ** 32) == 502539523
    assert r.nextLong(2 ** 40) == 269644638061
    assert r.nextLong() == 6146794652083548235


def test_nextBoolean():
    r = Random(seed=0)
    assert r.nextBoolean() is True
    assert r.nextBoolean() is True
    assert r.nextBoolean() is False
    assert r.nextBoolean() is True


def test_nextFloat():
    r = Random(seed=0)
    assert r.nextFloat() == 0.7309677600860596
    assert r.nextFloat() == 0.8314409852027893
    assert r.nextFloat() == 0.2405363917350769
    assert r.nextFloat() == 0.6063451766967773


def test_nextDouble():
    r = Random(seed=0)
    assert r.nextDouble() == 0.730967787376657
    assert r.nextDouble() == 0.24053641567148587
    assert r.nextDouble() == 0.6374174253501083
    assert r.nextDouble() == 0.5504370051176339


def test_nextGaussian():
    r = Random(seed=0)
    assert r.nextGaussian() == 0.8025330637390305
    assert r.nextGaussian() == -0.9015460884175122
    assert r.nextGaussian() == 2.080920790428163
    assert r.nextGaussian() == 0.7637707684364894


def test_ints():
    r_iter = Random(seed=0).ints()
    next_ints = [next(r_iter) for _ in range(5)]
    assert next_ints == [3139482720, 3571011896, 1033096058, 2604232894, 2737687030]


def test_longs():
    r_iter = Random(seed=0).longs()
    next_longs = [next(r_iter) for _ in range(5)]
    assert next_longs == [
        13483975612328137016,
        4437113785340752062,
        11758276261860732986,
        10153770766667359491,
        11022764866796693357,
    ]


def test_doubles():
    r_iter = Random(seed=0).doubles()
    next_doubles = [next(r_iter) for _ in range(5)]
    assert next_doubles == [
        0.730967787376657,
        0.24053641567148587,
        0.6374174253501083,
        0.5504370051176339,
        0.5975452777972018,
    ]
