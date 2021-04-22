# Web stuff

## Legacy serving

The `server.php` and `serve_dadguide_data.py` stuff are legacy, used to serve the initial iteration of the DadGuide API.
They're symlinked from the Apache web directory.

Hopefully this will eventually be deprecated and removed.

## Containers

We're trying to move towards running servers/pipelines in containers. This directory two holds Sanic Python webservers
that are containerized.

The *-api-cloudbuild.yaml files in the project root can be used to build the server containers.

The containers embed the database configuration; it's imported at build time using Secret Manager, the secret should be
named `prod_db_config` and should contain the standard `db_config.json`.

## Mobile server

Currently this is only used for development purposes, but I'd like to replace the shitty PHP stuff with it.

Main thing holding me back is:

1) The existing stuff seems to work fine
2) The server version keeps a connection open, as opposed to opening a fresh one (like the script does). I'm not sure
   how stable this is.
3) I have no monitoring set up for the new stuff. None for the old stuff either actually but empirically it seems to
   work.

To run the server on the DG host:

```bash
docker run -d --name mobile-api-server --network=host --restart=on-failure gcr.io/rpad-discord/mobile-api-server:latest
```

## Admin server

This serves the Monster Admin ES webapp, including the front end stuff and the API queries. Apache is reverse proxying
to this server.

The admin api server also needs a pointer to the on-disk ES dir, the local clone of the pad-game-data-slim repo.

Besides the python backend, it also includes a Flutter Web frontend. To run the cloudbuild script, you also need to have
compiled the Flutter Builder:
https://github.com/GoogleCloudPlatform/cloud-builders-community/tree/master/flutter

This should be updated periodically.

To run the server on the DG host:

```bash
docker run -d --name admin-api-server --network=host --restart=on-failure -v /home/bot/dadguide/pad-game-data:/server/es gcr.io/rpad-discord/admin-api-server:latest
```

I had trouble getting the build args and runtime args to play nicely with the entrypoint, so the ES dir is hardcoded.
The bind mount to `/server/es` is a hard requirement.

## Building the containers

Run these commands from the root of the project.

### On Cloud Build

```bash
gcloud builds submit . --config=admin-api-server-cloudbuild.yaml 
```

## Local compilation

After following the instructions here:
https://cloud.google.com/cloud-build/docs/build-debug-locally

```bash
cloud-build-local --dryrun=false  --config=admin-api-server-cloudbuild.yaml  .
```

## Continuous deployment

Watchtower is set up to continuously deploy new builds:

```bash
docker run -d --name watchtower --restart always -v /home/bot/.docker/config.json:/config.json -v /var/run/docker.sock:/var/run/docker.sock v2tec/watchtower -i 30
```

Watchtower needs to have authorization to GCR. To set up auth:

Create a service account, and ensure it has Storage Viewer access. Get a json key file and save it into `~/.docker/`:
https://cloud.google.com/container-registry/docs/advanced-authentication#json-key

Run:

```bash
docker login -u _json_key --password-stdin https://gcr.io < ~/.docker/gcloudauth.json
```
