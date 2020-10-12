=======
MC Maps
=======

WSGI Python backend and JavaScript library for generating maps on https://mcmaps.io/.

This project is an attempt to provide a service capable server and compatible client library similar to the services provided by Google Maps but for Minecraft world generation via Python WSGI and transpiled ES6 JavaScript.

Installation
------------

* Clone the repo via git ``https://github.com/LanetheGreat/mcmaps.git``.
* Install the required python packages using pipenv for the Python portion of the project via "``pipenv install``" or "``python -m pipenv install``".
* Install the required node packages for the JavaScript portion of the project via "``npm install``".
* Transpile the main site Javascript and library via the commands "``npm run build-app``" and "``npm run build-lib``".
* Use the provided Apache .conf example file (``mcmaps_apache.conf.example``) to configure Apache as your WSGI server, replacing the defined variables and server admin email.

 - *Note: The provided configuration by default expects a non-privileged user called "mc" to exist on your system.*
 - Replace the defined "docroot" value with the location of the cloned project folder.
 - Replace the defined "domain" value with the URL used by your DNS provider or hosting service.
 - Replace the defined "site_user" value with the user id or name that the Python scripts will be run as.
 - Replace the defined "site_group" value with the group id or name that the Python scripts will be run as.
 - Replace the defined "python_venv" value with the path to your site's virtual environment folder, otherwise if you're not using one remove "``python-home=${python_venv}``" from line 23 (WSGIDaemonProcess config line).
 - Replace the "ServerAdmin" email with your admin email.

Development
-----------

* Use the command ``npm run start-dev-servers`` to start both of the cherrypy WSGI and Webpack developmental servers, the webpage should automatically open your browser to http://localhost:3000/ to view the local development instance of the site.
* Refresh the page after making any Python or JavaScript code changes to preview them.
