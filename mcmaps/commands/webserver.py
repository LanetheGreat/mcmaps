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

''' Development webserver command to aid in local development and testing. '''

__all__ = ['webserver_run']

import cherrypy
from cherrypy.lib.static import serve_file
from pathlib import Path

from . import subparsers  # @UnresolvedImport


class Root:
    path = Path(__file__).parent.parent

    @cherrypy.expose
    def index(self):
        return serve_file(str(self.path / 'index.html'))


def webserver_run(args):
    from mcmaps.wsgi import apps
    from webbrowser import open_new_tab

    for app in apps:
        cherrypy.tree.graft(app, '/api/' + app.__module__.split('.')[-1])

    host = args.host or '127.0.0.1'
    port = args.port or 3001

    if args.open:
        if port == 80:
            open_new_tab(f'http://{host}/')
        else:
            open_new_tab(f'http://{host}:{port}/')

    cherrypy.config.update({
        'server.socket_host': host,
        'server.socket_port': port,
    })

    cherrypy.quickstart(Root(), '/', {
        '/assets/dist': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': str(Root.path / 'assets' / 'dist'),
        },
    })


SERVER_CMDS = {
    'run': webserver_run,
}

server_cmd = subparsers.add_parser('webserver', help='development server commands')
server_cmd.add_argument('-H', '--host', default='127.0.0.1')
server_cmd.add_argument('-P', '--port', default=3001, type=int)
server_cmd.add_argument('-o', '--open', action='store_true')
server_cmd.add_argument('command', metavar='command', type=str.lower, choices=SERVER_CMDS, nargs='?', default='run', help='Supported commands: ' + ', '.join(SERVER_CMDS))
server_cmd.set_defaults(command_func=lambda x: SERVER_CMDS[x.command](x))
