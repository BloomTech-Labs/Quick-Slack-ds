
FROM python:3.7.6-buster

RUN apt-get update && apt-get install -qq -y \
        curl \
        gnupg

RUN echo "deb [arch=amd64] http://storage.googleapis.com/tensorflow-serving-apt stable tensorflow-model-server tensorflow-model-server-universal" | tee /etc/apt/sources.list.d/tensorflow-serving.list

ENV APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE 1
ENV TF_CPP_MIN_LOG_LEVEL 2
RUN curl -s https://storage.googleapis.com/tensorflow-serving-apt/tensorflow-serving.release.pub.gpg | apt-key add -

RUN apt-get update && apt-get install -y tensorflow-model-server

RUN  apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /home

ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN pip install --editable .

CMD tensorflow_model_server --port=8500 --rest_api_port=8501 --model_config_file=configs/models.conf