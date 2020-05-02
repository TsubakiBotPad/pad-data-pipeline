FROM python:3.6-slim-buster

ARG SCRIPT_NAME
ARG EXTRA_ARG
ARG PORT

# slim-buster is 150MB lighter than python:3.6 but does not include git, which we need.
RUN apt-get update && \
    apt-get install -y git

# The Cloud Build script should have populated the directory properly.
ADD . /server/

# Install Python dependencies
RUN python3 -m pip install -r /server/requirements.txt

# Expose the HTTP port we're listening on
EXPOSE ${PORT}

# The python deps are installed to this directory.
WORKDIR /server

# Create a script to pass build-time command line args to python
RUN echo "python3 /server/${SCRIPT_NAME} --port=${PORT} --db_config=/server/db_config.json ${EXTRA_ARG} \$@" > /run_server.sh

# Default entrypoint that runs the script, which allows for extra args to be passed at run time
ENTRYPOINT ["/bin/bash", "/run_server.sh"]
