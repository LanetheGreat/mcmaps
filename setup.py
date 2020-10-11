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
mcmaps: WSGI Python backend and JavaScript library for generating maps on https://mcmaps.io/.

Note that "python setup.py test" invokes pytest on the package. With appropriately
configured setup.cfg, this will check both xxx_test modules and docstrings.
'''

import json, sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


# This is a plug-in for setuptools that will invoke py.test
# when you run python setup.py test
class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest  # import here, because outside the required eggs aren't loaded yet
        sys.exit(pytest.main(self.test_args))


with open('package.json') as package_meta:
    version = json.load(package_meta)['version']

setup(
    name="mcmaps",
    version=version,
    description="WSGI Python backend and JavaScript library for generating maps on https://mcmaps.io/.",
    long_description=open("README.rst").read(),
    classifiers=[  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 1 - Planning',
        'Programming Language :: Python'
    ],
    keywords="Python JavaScript Minecraft map maps world generation WSGI",  # Separate with spaces
    author="Lane Shaw",
    author_email="lshaw.tech@gmail.com",
    url="https://mcmaps.io/",
    license="Apache-2.0",
    packages=find_packages(exclude=['examples', 'tests']),
    include_package_data=True,
    zip_safe=True,
    tests_require=['pytest'],
    cmdclass={'test': PyTest},

    # TODO: List of packages that this one depends upon:
    install_requires=[],
)
