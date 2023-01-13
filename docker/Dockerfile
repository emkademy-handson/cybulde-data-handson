FROM python:3.9-slim

ARG USER_ID=1000
ARG USER_NAME=kyuksel
ENV HOME=/home/$USER_NAME
ENV \
    PYTHONBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    TZ=Europe/Warsaw \
    VIRTUAL_ENV=$HOME/venv \
    PATH="/usr/local/gcloud/google-cloud-sdk/bin:$HOME/venv/bin:$PATH" \
    PYTHONPATH="/app:$PYTHONPATH" \
    BUILD_POETRY_LOCK="$HOME/poetry.lock.build"

RUN apt-get -qq update \
    && apt-get -qq -y install vim gcc curl git build-essential libb64-dev graphviz software-properties-common sqlite3 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get -qq -y clean

# Install gcloud and gsutil
RUN curl https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-396.0.0-linux-x86_64.tar.gz > /tmp/google-cloud-sdk.tar.gz
RUN mkdr -p /usr/local/gcloud \
    && tar -C /usr/local/gcloud -xf /tmp/google-cloud-sdk.tar.gz \
    && /usr/local/gcloud/google-cloud-sdk/install.sh --usage-reporting false --command-completion true --bash-completion true --path-update true --quiet

RUN addgroup --system --gid $USER_ID $USER_NAME \
    && useradd --system -m --no-log-init --home-dir $HOME --uid $USER_ID --gid $USER_NAME --groups $USER_NAME $USER_NAME

RUN chown -R $USER_NAME $HOME
RUN mkdir -p /app && chown $USER_NAME /app /tmp

RUN HOME=/tmp python3.9 -m pip install poetry==1.2.2

USER $USER_NAME

COPY pyproject.toml *.lock /app
WORKDIR /app

RUN python3.9 -m venv $VIRTUAL_ENV \
    && pip install --upgrade pip setuptools \
    && poetry install \
    && cp poetry.lock $BUILD_POETRY_LOCK \
    && rm -rf $HOME/.cache/*

RUN python3.9 -m nltk.downloader stopwords && python3.9 -m nltk.downloader punkt

USER root
COPY ./docker/scripts/* /
RUN chown -R $USER_NAME /*.sh && chmod +x /*.sh
USER $USER_NAME

COPY . /app/
CMD ["/startup-script.sh"]
