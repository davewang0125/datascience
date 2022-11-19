FROM python:3.8

ENV ONLINE_MODE true
ENV EVAL_ENGINE_NAME nutcracker
ENV EVAL_ENGINE_VERSION online-1.0-88394fb2
ENV ASR_HOST nutcracker.asr-evaluation.svc.cluster.local
ENV ASR_PORT 50051
ENV LANGUAGE_CODE es-ES
ENV AUDIO_SET_ID 00000000-0000-0000-0000-000000000000

ENV PGUSER asr-eval
ENV PGPASSWORD dummy-passwd
ENV PGHOST 127.0.0.1
ENV PGPORT 5432
ENV PGDATABASE asr-eval

ENV AWS_ACCESS_KEY_ID dummy-id
ENV AWS_SECRET_ACCESS_KEY dummy-secret
ENV TRAINABLE_VOICEA_CLIENT_ID dummy-id
ENV TRAINABLE_VOICEA_CLIENT_SECRET dummy-secret

ENV AUTH_URL https://api.uswest1-0.cprod.vcra.co/oauth/token
ENV TRAINABLE_URL https://trainable.uswest1-0.cprod.vcra.co
ENV CHUNK_SIZE 8096

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

ENTRYPOINT /src/scripts/docker-entry.sh
