#FROM python:3.6-slim-buster
FROM python:3.6

ADD . /server/
RUN python3 -m pip install -r /server/requirements.txt

EXPOSE 8000
ENTRYPOINT ["python3", "/server/server.py"]
