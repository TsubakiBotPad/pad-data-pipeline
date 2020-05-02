# Web stuff

## Legacy serving

The `server.php` and `serve_dadguide_data.py` stuff are legacy, used to serve
the initial iteration of the DadGuide API. They're symlinked from the Apache
web directory.

Hopefully this will eventually be deprecated and removed.

## Containers

We're trying to move towards running servers/pipelines in containers. This
directory two holds Sanic Python webservers that are containerized.

The *-api-cloudbuild.yaml files in the project root can be used to build the
server containers.

The containers embed the database configuration; it's imported at build time
using Secret Manager, the secret should be named `prod_db_config` and should
contain the standard `db_config.json`.

## Mobile server

Currently this is only used for development purposes, but I'd like to replace
the shitty PHP stuff with it.

Main thing holding me back is:
1) The existing stuff seems to work fine
2) The server version keeps a connection open, as opposed to opening a fresh
one (like the script does). I'm not sure how stable this is.
3) I have no monitoring set up for the new stuff. None for the old stuff either
actually but empirically it seems to work. 

## Admin server

This serves the Monster Admin ES webapp, including the front end stuff and the
API queries. Apache is reverse proxying to this server.

The admin api server also needs a pointer to the on-disk ES dir, the local
clone of the pad-game-data-slim repo.

Besides the python backend, it also includes a Flutter Web frontend. To run the
cloudbuild script, you also need to have compiled the Flutter Builder:
https://github.com/GoogleCloudPlatform/cloud-builders-community/tree/master/flutter

This should be updated periodically.
