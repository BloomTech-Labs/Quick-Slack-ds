# syntax = docker/dockerfile:experimental
FROM python:3.7.6-buster

RUN --mount=type=cache,target=/var/cache/apt --mount=type=cache,target=/var/lib/apt apt-get update \
	&& apt-get install -qq -y build-essential libpq-dev python3-setuptools --no-install-recommends

ENV INSTALL_PATH /flask
RUN mkdir $INSTALL_PATH
WORKDIR $INSTALL_PATH

ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

COPY . .

RUN pip install --editable .
RUN useradd flask
RUN chown flask:flask .
USER flask
CMD gunicorn -c "python:config.gunicorn" "quickslack.app:create_app()"