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

''' Starts a CherryPy server to aid in local development and testing '''

import cherrypy
from cherrypy.lib.static import serve_file
from mcmaps.wsgi import apps
from pathlib import Path


class Root:
    path = Path(__file__).parent.parent

    @cherrypy.expose
    def index(self):
        return serve_file(str(self.path / 'index.html'))


for app in apps:
    cherrypy.tree.graft(app, '/api/' + app.__module__.split('.')[-1])

cherrypy.quickstart(Root(), '/', {
    '/assets/dist': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': str(Root.path / 'assets' / 'dist'),
    }
})
