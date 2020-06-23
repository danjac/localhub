# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

FROM python:3.8.3-buster

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER=1
ENV PYTHONHASHSEED=random
ENV DISABLE_COLLECTSTATIC=1

RUN apt-get update \
    && apt-get install --no-install-recommends -y postgresql-client-11 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements/base.txt /requirements/base.txt
COPY ./requirements/aws.txt /requirements/aws.txt
COPY ./requirements/heroku.txt /requirements/heroku.txt

RUN pip install -r requirements/heroku.txt

WORKDIR /app
COPY . /app

RUN useradd -m user
USER user
