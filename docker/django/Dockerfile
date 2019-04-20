FROM python:3.7-alpine

ENV PYTHONUNBUFFERED 1

RUN apk update \
      && apk add --virtual build-deps gcc python3-dev musl-dev \
      && apk add postgresql-dev \
      && apk add libffi-dev py-cffi \
      && apk add gettext \
      && apk add postgresql-client

# Copy requirements to insure caching
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

WORKDIR /app

COPY ./docker/django/startapp /startapp
RUN chmod +x /startapp
