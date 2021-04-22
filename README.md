# dadguide-data

## Looking for exported data?

Skip the rest of this and look in the `utils` directory for scripts that will let you access the exports, including the
raw data and processed database.

## What's in here

`docker` : Easier development setup in docker.

`etl` : Contains the most important stuff, downloading, parsing, and processing the PAD game data.

`images` : Image files used by DadGuide, latents, awakenings, etc. No monster icons/portraits.

`media_pipelines` : Code for extracting and processing PAD media, including icons, portraits, voice lines, animations,
etc.

`proto` : Protocol buffer definitions used by the pipeline and DadGuide (mostly for enemy skills).

`schema` : Stuff to do with mysql specifically.

`utils` : Some random scripts for development purposes. If you want to access data exports, look here.

`web` : The 'admin api' and 'mobile api' sanic servers, plus some stuff that serves the DadGuide API in prod.

In the root directory are some Google Cloud Build files for building the mobile/api servers, and the requirements file
that you should install if you want to use the ETL pipeline.

## Database setup

MySql is used as a backend on the server, and SQLite on the mobile app. You can install the server yourself:

```bash
sudo apt install mysql-workbench
sudo apt install mysql-server
```

The `utils` folder has some scripts to download the exports and populate the databse.

Alternatively you can use a docker script to start it up (see below).

### Docker based development

In the `docker` directory are utilities to help you get working faster. You can download the database backup from
production, start a mysql container, and restore the backup with a single command:

```bash
docker/start_env.sh
```

## Pipeline testing

The utils directory contains a script called `data_exporter.py`. This script is run to generate the
repository: https://github.com/nachoapps/pad-game-data-slim

The server has a cron job which runs this periodically, commits, and pushes.

If you're making changes, you should check out a copy of `pad-game-data-slim` at head and run the data exporter locally
to confirm your changes had the effect you expected.

## API testing

Production uses an Apache webserver with PHP that executes a python script.

Development uses a sanic webserver (requires python 3.6 and sanic\_compress). Eventually production should
probably `mod_proxy` through to this.

The files used for both are in the `web` directory.

### Google Cloud Build pull-tests

This didn't work well and is currently disabled. Should be re-enabled with just writing the `data_exporter.py` results
and making sure it does not crash, probably.

### Future tests

It would be really great to have a version that either did the mysql data load, or a sqlite one, or maybe just dumps the
computed SQL to a file. The latter is probably not sufficient, since some steps require index lookups and we would have
to fake those.
