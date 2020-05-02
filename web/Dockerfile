FROM python:3.6-slim-buster

ARG SCRIPT_NAME
ENV SCRIPT_NAME=${SCRIPT_NAME}
ARG EXTRA_ARG
ENV EXTRA_ARG=${EXTRA_ARG}

RUN apt-get update && \
    apt-get install -y git

ADD . /server/
RUN python3 -m pip install -r /server/requirements.txt

EXPOSE 8000
ENTRYPOINT python3 /server/${SCRIPT_NAME} --db_config=/server/db_config.json ${EXTRA_ARG}
