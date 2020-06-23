# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

FROM python:3.8.3-buster

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER=1
ENV PYTHONHASHSEED=random

RUN apt-get update \
    && apt-get install --no-install-recommends -y postgresql-client-11 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements/base.txt /requirements/base.txt
COPY ./requirements/test.txt /requirements/test.txt
COPY ./requirements/local.txt /requirements/local.txt

RUN pip install -r requirements/local.txt

WORKDIR /app

COPY ./scripts/entrypoint /entrypoint
RUN chmod +x /entrypoint

COPY ./scripts/start-django /start-django
RUN chmod +x /start-django

COPY ./scripts/start-celeryworker /start-celeryworker
RUN chmod +x /start-celeryworker

ENTRYPOINT ["/entrypoint"]
