# syntax = docker/dockerfile:experimental
FROM nvidia/cuda:10.1-runtime-ubuntu18.04
RUN --mount=type=cache,target=/var/cache/apt --mount=type=cache,target=/var/lib/apt apt-get update\
 && apt-get install python3 python3-pip postgresql-client build-essential -y
RUN ln -s /usr/bin/pip3 /usr/bin/pip
RUN ln -s /usr/bin/piython3 /usr/bin/python


COPY requirements.txt requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

ENV WORK_DIR /notebooks
RUN mkdir $WORK_DIR
WORKDIR $WORK_DIR

COPY . .
RUN useradd nbserver -m
RUN chown nbserver:nbserver . -R
USER nbserver
