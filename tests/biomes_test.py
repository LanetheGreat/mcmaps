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

import os
from collections import OrderedDict

from mcmaps._testing import IndentedXMLGenerator
from mcmaps.mc.biomes import initialize_all_biomes
from mcmaps.mc.constants import WORLD_TYPE

TEST_X_RANGE = range(-256, 257, 16)
TEST_Z_RANGE = range(-1024, 1, 16)

def test_biomes():
    import filecmp
    fixture_path = os.path.join('tests', 'fixtures', 'identity_world_biomes.xml')
    test_path = os.path.join('tests', 'fixtures', 'identity_world_biomes.test.xml')

    with open(test_path, 'w', encoding='utf-8') as xml_file:
        xml = IndentedXMLGenerator(
            xml_file, encoding='utf-8', short_empty_elements=True,
            indentation='    ', xml_declaration=False,
        )

        # Prepare a generator for the identity world (Seed=0) with debug enabled.
        biome_generator, _ = initialize_all_biomes(0, WORLD_TYPE.DEFAULT, debug=xml)

        xml.startDocument()
        xml.startElement('chunks', {})

        for x in TEST_X_RANGE:
            for z in TEST_Z_RANGE:
                xml.startElement('chunk', OrderedDict((
                    ('x', str(x)),
                    ('z', str(z)),
                    ('width', '16'),
                    ('depth', '16'),
                )))
                biome_generator.get_area(x, z, 16, 16)
                xml.endElement('chunk')

        xml.endElement('chunks')
        xml.endDocument()

    # Check if the layer output matches the identity world's partial generation.
    assert filecmp.cmp(fixture_path, test_path, shallow=False)
    os.remove(test_path)


def test_indexes():
    import filecmp
    fixture_path = os.path.join('tests', 'fixtures', 'identity_world_indexes.xml')
    test_path = os.path.join('tests', 'fixtures', 'identity_world_indexes.test.xml')

    with open(test_path, 'w', encoding='utf-8') as xml_file:
        xml = IndentedXMLGenerator(
            xml_file, encoding='utf-8', short_empty_elements=True,
            indentation='    ', xml_declaration=False,
        )

        # Prepare a generator for the identity world (Seed=0) with debug enabled.
        _, index_generator = initialize_all_biomes(0, WORLD_TYPE.DEFAULT, debug=xml)

        xml.startDocument()
        xml.startElement('chunks', {})

        for x in TEST_X_RANGE:
            for z in TEST_Z_RANGE:
                xml.startElement('chunk', OrderedDict((
                    ('x', str(x)),
                    ('z', str(z)),
                    ('width', '16'),
                    ('depth', '16'),
                )))
                index_generator.get_area(x, z, 16, 16)
                xml.endElement('chunk')

        xml.endElement('chunks')
        xml.endDocument()

    # Check if the layer output matches the identity world's partial generation.
    assert filecmp.cmp(fixture_path, test_path, shallow=False)
    os.remove(test_path)


if __name__ == '__main__':
    test_biomes()
    test_indexes()
