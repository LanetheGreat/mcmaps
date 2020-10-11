=======
MC Maps
=======

WSGI Python backend and JavaScript library for generating maps on https://mcmaps.io/.

This project is an attempt to provide a service capable server and compatible client library similar to the services provided by Google Maps but for Minecraft world generation via Python WSGI and transpiled ES6 JavaScript.

Installation
------------

* Clone the repo via git ``https://github.com/LanetheGreat/mcmaps.git``.
* Install the required python packages using pipenv for the Python portion of the project via ``pipenv install``.
* Install the required node packages for the JavaScript portion of the project via ``npm install``.
* Transpile the main site Javascript via the command ``npm run build-app``.

 - Optionally transpile the client-side library via ``npm run build-lib``.

* Use the provided Apache .conf example file (``mcmaps_apache.conf.example``) to configure Apache as your WSGI server, eplacing the defined variables and server admin email.

 - Replace the defined "docroot" value with the location of the cloned project folder.
 - Replace the defined "domain" value with the URL used by your DNS provider or hosting service.
 - Replace the "ServerAdmin" email with your admin email.

Development
-----------

* Use the command ``npm run start-dev-servers`` to start both of the cherrypy WSGI and Webpack developmental servers, the webpage should automatically open your browser to http://localhost:3000/ to view the local development instance of the site.
* Refresh the page after making any Python or JavaScript code changes to preview them.
