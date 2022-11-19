FROM python:3.8


## should be replaced with mysql
ENV PGUSER asr-eval
ENV PGPASSWORD dummy-passwd
ENV PGHOST 127.0.0.1
ENV PGPORT 5432
ENV PGDATABASE asr-eval

ENV AWS_ACCESS_KEY_ID dummy-id
ENV AWS_SECRET_ACCESS_KEY dummy-secret

RUN apt update && apt install -y \
    git \
    sox \
    python3-opencv \
    ffmpeg \
    vim \
    protobuf-compiler \
    awscli && \
    mkdir -p /src/

COPY . /src/
WORKDIR /src/
RUN pip3 install -U -r requirements.txt
RUN pip3 install -U -r common-flow/requirements.txt
RUN python3 -c 'import nltk; nltk.download("punkt")'
RUN apt -y install postgresql
RUN chmod +x scripts/docker-entry.sh && chmod ugo+x scripts/run-tests.sh

RUN useradd -rm -d /home/test_user -s /bin/bash -g root -G sudo -u 1001 test_user

ENTRYPOINT python server.py
