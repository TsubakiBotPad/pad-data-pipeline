# dadguide-data

## Database setup

```bash
sudo apt install mysql-workbench
sudo apt install mysql-server

```

You can use `utils/download_db_from_prod.sh` and `utils/restore_db_from_prod` to download the
exported database and install it into your local copy.


## Local testing

In prod we're using a Apache webserver with PHP that executes a python script. Kind of gross.

In dev we're using a sanic webserver (requires python 3.6 and sanic\_compress). It would be nice
to start using this in prod using mod\_proxy? 

## Integration tests

In `tests/parser_integration_test.py` we've got a test that loads all the raw data and saves the
'cross server' parsed outputs, then compares against a golden copy. Get the raw data using
`utils/refresh_data` first.

If you're making a change, you should run this once, then make your change, then run it again.
You can use the diff to confirm your changes.

### Google Cloud Build pull-tests

Whenever a PR is opened, a trigger should execute the integration test using GCB. This compares
against golden files saved to GCS.

You can test locally or on GCB using the following commands:

```bash
PYTHONPATH=etl python3 tests/parser_integration_test.py --input_dir=pad_data/raw --output_dir=pad_data/integration
cloud-build-local --config=pit-cloudbuild.yaml --dryrun=false .
gcloud builds --config=pit-cloudbuild.yaml  .
```

The GCB-based tests run against a snapshot of the raw and golden data. If you're happy with any
local changes, after running the integration tests use the following commands to update the
golden set:

```bash
gsutil -m cp -r -c pad_data/integration/new gs://dadguide-integration/parser/golden
gsutil -m cp -r -c pad_data/raw gs://dadguide-integration/parser/raw
```

### Future tests

It would be really great to have a version that either did the mysql data load, or a sqlite one, or
maybe just dumps the computed SQL to a file. The latter is probably not sufficient, since some steps
require index lookups and we would have to fake those.

### Docker based development

In the `docker` directory are utilities to help you get working faster. You can download the database
backup from production, start a mysql container, and restore the backup with a single command:

```bash
docker/start_env.sh
```

TODO: start the sanic webserver as well for ease of dadguide-flutter dev work

TODO: docker script to launch the pipeline against the docker env