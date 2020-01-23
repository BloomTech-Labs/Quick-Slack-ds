# syntax = docker/dockerfile:experimental
FROM python:3.7.6-buster

ENV INSTALL_PATH /api
RUN mkdir $INSTALL_PATH
WORKDIR $INSTALL_PATH

ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

COPY . .

CMD gunicorn -c "python:config.gunicorn" "api.app:create_app()"