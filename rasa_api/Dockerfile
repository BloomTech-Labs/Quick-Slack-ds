# syntax = docker/dockerfile:experimental
FROM python:3.7.6-buster

ENV INSTALL_PATH /rasa_api
RUN mkdir $INSTALL_PATH
WORKDIR $INSTALL_PATH

ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

COPY . .
RUN useradd rasa -m
RUN chown rasa:rasa . -R
USER rasa
CMD rasa run